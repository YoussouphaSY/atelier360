from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Atelier360.models import Activite, Article, LigneReservation, Reservation
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Reservation, Article, LigneReservation
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
        articles_data = [{
            'id': article.id,  # Ajoutez l'ID pour chaque article
            'nom': article.nom,
            'description': article.description
        } for article in articles]
        return JsonResponse({'articles': articles_data}, safe=False)

    # Retourne une erreur plus explicite si la méthode est incorrecte
    return JsonResponse({'error': 'Méthode HTTP invalide. Utilisez GET.'}, status=405)


@csrf_exempt
def create_reservation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            activite_id = data.get('activite')
            article_id = data.get('articles')
            quantite = int(data.get('quantity'))

            # Valider les données reçues
            if not activite_id or not article_id or quantite <= 0:
                return JsonResponse({'success': False, 'message': 'Données invalides.'})

            activite = Activite.objects.get(id=activite_id)
            article = Article.objects.get(id=article_id)

            # Créer une réservation
            reservation = Reservation.objects.create(
                nom=f"Réservation pour {activite.nom}",
                activite=activite,
                dateDebut=now()
            )

            # Créer une ligne de réservation
            LigneReservation.objects.create(
                reservation=reservation,
                article=article,
                quantiteDemande=quantite,
                quantiteValider=0, 
                dateDebut=now(),
                dateFin=now()
            )

            return JsonResponse({'success': True, 'message': 'Réservation créée avec succès.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


def reserver(request):
    if request.method == 'POST':
        # Obtenez l'activité associée (par exemple, depuis le formulaire ou une valeur par défaut)
        activite_id = request.POST.get('activite_id')  # Récupérer l'ID de l'activité à réserver
        activite = Activite.objects.get(id=activite_id)
        
        # Créez la réservation
        reservation = Reservation.objects.create(
            nom=f"Réservation pour {activite.nom}",  # Génère un nom basé sur l'activité
            activite=activite
        )
        
        # Renvoyer une réponse JSON ou rediriger selon votre besoin
        return JsonResponse({'success': True, 'reservation_id': reservation.id})

    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=400)


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