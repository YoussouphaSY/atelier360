from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Atelier360.models import Activite, Article, LigneReservation, Reservation
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Formateur, Reservation, Article, LigneReservation, Notification
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from django.contrib.auth import logout


# views pour gerer les connexions
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username') 
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)  # Authentifier avec username

            if user is not None:
                auth_login(request, user)
                if user.is_superuser:
                    # Vérification si c'est un superutilisateur
                    # redirection vers la page admin
                    return redirect('admin:index')
                elif user.role in ['formateur', 'metier', 'gestionnaire']:
                    # redirection vers la page Accueil si ce n'est pas un superutilisateur
                    return redirect('home')
                else:
                    # redirection vers la page erreur si rôle non identifié
                    return redirect('page')
            else:
                form.add_error(None, "Nom d'utilisateur ou mot de passe incorrect")
    else:
        form = LoginForm()

    return render(request, 'Atelier360/login.html', {'form': form})


# Décorateur pour vérifier si l'utilisateur est connecté et a un rôle spécifique
# Page d'acceuil
@login_required
@user_passes_test(lambda user: user.role in ['formateur', 'gestionnaire'], login_url='page')
def home_view(request):
    # Récupération des activités avec leurs relations
    activities = Activite.objects.select_related(
        'planning',
        'planning__metier',
        'planning__metier__departement'
    ).all()

    context = {
        'activities': activities,
        'user': request.user
    }
    
    return render(request, 'Atelier360/home.html', context)


@login_required
def page_view(request):
    return render(request, 'Atelier360/page.html')


@login_required
def profil(request):
    return render(request, 'Atelier360/profil.html')


# Vue pour afficher le profil de l'utilisateur
@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'Atelier360/profile.html', context)


@login_required
def mes_reservations(request):
    # Récupérer le paramètre 'activite_id' de la requête GET
    activite_id = request.GET.get('activite_id')  # Peut-être 'activite_id' dans l'URL, ou dans les paramètres de requête

    if activite_id:
        # Filtrer les réservations en fonction de l'activité
        reservations = Reservation.objects.filter(activite_id=activite_id).select_related('activite')
    else:
        # Si aucun activite_id n'est passé, récupérer toutes les réservations
        reservations = Reservation.objects.all().select_related('activite')

    context = {
        'reservations': reservations
    }
    return render(request, 'Atelier360/mes_reservations.html', context)


@login_required
def planning(request):
    return render(request, 'Atelier360/planning.html')


@login_required
def notifications(request):
    return render(request, 'Atelier360/notifications.html')


@csrf_exempt
def get_articles(request):
    if request.method == 'GET':
        articles = Article.objects.all()
        articles_data = [{'nom': article.nom, 'description': article.description} for article in articles]
        return JsonResponse({'articles': articles_data}, safe=False)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Reservation, Activite, Article
from .serializers import ReservationSerializer

@api_view(['POST'])
def create_reservation(request):
    try:
        activity_id = request.data.get('activity_id')
        quantity = request.data.get('quantity')
        articles = request.data.get('articles')
        start_date = request.data.get('startDate')

        # Vérification de la présence des champs nécessaires
        if not all([activity_id, quantity, articles, start_date]):
            return Response({'detail': 'Données manquantes'}, status=400)

        try:
            activity = Activite.objects.get(id=activity_id)
        except Activite.DoesNotExist:
            return Response({'detail': 'Activité non trouvée'}, status=400)

        try:
            article = Article.objects.get(id=articles)
        except Article.DoesNotExist:
            return Response({'detail': 'Article non trouvé'}, status=400)

        # Création de la réservation
        reservation = Reservation.objects.create(
            activity=activity,
            article=article,
            quantity=quantity,
            start_date=start_date
        )

        return Response({'success': True}, status=201)
    except Exception as e:
        return Response({'detail': str(e)}, status=400)


@csrf_exempt
def add_reservation_detail(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Exemple de données attendues
            # {
            #     "reservation_id": 1,
            #     "article_id": 2,
            #     "quantity": 5
            # }

            reservation_id = data.get('reservation_id')
            article_id = data.get('article_id')
            quantity = data.get('quantity')

            # Vérifiez si la réservation et l'article existent
            reservation = get_object_or_404(Reservation, id=reservation_id)
            article = get_object_or_404(Article, id=article_id)

            # Créez une ligne de réservation
            ligne_reservation = LigneReservation.objects.create(
                reservation=reservation,
                article=article,
                quantity=quantity
            )

            return JsonResponse({"success": True, "line_id": ligne_reservation.id}, status=201)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_activity(request, activity_id):
    try:
        activity = Activite.objects.get(id=activity_id)
        return JsonResponse({
            'id': activity.id,
            'nom': activity.nom,  # Utiliser 'nom' ici, comme défini dans votre modèle
            'salle': activity.salle,
            'dateDebut': activity.dateDebut.isoformat(),  # Convertir la date en format ISO
            # Vous pouvez également ajouter d'autres informations comme la salle ou le planning
            'planning': activity.planning.id  # Exemple pour inclure l'ID du planning associé
        })
    except Activite.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)


def deconnexion(request):
    logout(request)  # Déconnecte l'utilisateur
    return redirect('login')