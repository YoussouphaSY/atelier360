# Importations nécessaires
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Atelier360.models import Activite, Article, Attribution, LigneAttribution, LigneReservation, Planning, Reservation, Notification
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from django.contrib.auth import logout
from django.db.models import Sum


# views pour gerer les connexions
def user_login(request):
    
    """
    Gère la connexion des utilisateurs en fonction de leur rôle.
    Redirige les utilisateurs vers des pages spécifiques selon leur rôle.
    """

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username') 
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)  # Authentifier avec username

            if user is not None:
                auth_login(request, user)
                if user.is_superuser:
                    return redirect('admin:index')  # Redirection pour les superutilisateurs
                elif user.role in ['metier', 'gestionnaire']:
                    return redirect('admin:index')  # Redirection pour ces rôles vers l'admin
                elif user.role == 'formateur':
                    return redirect('home')  # Redirection pour les formateurs
                else:
                    return redirect('page')  # Page d'erreur pour les rôles inconnus
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

    """
    Affiche la page d'accueil pour les utilisateurs autorisés (formateurs ou gestionnaires).
    Charge les activités liées à l'utilisateur connecté.
    """

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
    """
    Affiche les réservations de l'utilisateur connecté avec leurs lignes associées.
    La quantité validée est incluse pour chaque ligne.
    """
    # Récupérer le paramètre 'activite_id' de la requête GET
    activite_id = request.GET.get('activite_id')

    # Récupérer les réservations avec ou sans filtre par activité
    if activite_id:
        reservations = Reservation.objects.filter(
            activite_id=activite_id
        ).select_related('activite')
    else:
        reservations = Reservation.objects.all().select_related('activite')

    # Préparer les données à envoyer au template
    reservation_data = []
    for reservation in reservations:
        lignes = []
        ligne_reservations = LigneReservation.objects.filter(reservation=reservation)
        for ligne in ligne_reservations:
            try:
                ligne_attribution = LigneAttribution.objects.get(
                    attribution__reservation=reservation,
                    attribution__article=ligne.article
                )
                quantite_validee = ligne_attribution.quantiteValider
            except LigneAttribution.DoesNotExist:
                quantite_validee = 0  # Pas de quantité validée

            lignes.append({
                "id": ligne.id,
                "article_nom": ligne.article.nom,
                "quantite_demande": ligne.quantiteDemande,
                "quantite_validee": quantite_validee,
                "article_id": ligne.article.id,
            })

        reservation_data.append({
            "activite_nom": reservation.activite.nom,
            "activite_sale": reservation.activite.sale,
            "date_debut": reservation.dateDebut,
            "statut": reservation.statut,
            "lignes": lignes,
        })

    # Passer les données au template
    context = {
        "reservations": reservation_data,
    }
    return render(request, "Atelier360/mes_reservations.html", context)



@login_required
def get_planning_events(request):
    """
    Vue pour afficher le planning dans un template HTML.
    """
    plannings = Planning.objects.prefetch_related(
        'activites', 
        'metier', 
        'metier__departement'
    )

    # Préparer les données pour le template
    events = []
    for planning in plannings:
        events.append({
            'id': planning.id,
            'nom': planning.nom,
            'dateDebut': planning.dateDebut,
            'dateFin': planning.dateFin,
            'metier': planning.metier.nom,
            'departement': planning.metier.departement.nom,
            'activites': planning.activites.all(),  # On peut passer les objets directement
        })

    # Envoyer les données au template
    return render(request, 'Atelier360/planning.html', {'plannings': events})



@login_required
def notifications(request):
    return render(request, 'Atelier360/notifications.html')


@csrf_exempt
def get_articles(request):
    
    """
    API pour récupérer la liste des articles disponibles.
    Retourne les articles au format JSON.
    """
    
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

    """
    API pour créer une réservation.
    Valide les données envoyées, vérifie la disponibilité et enregistre la réservation.
    """
 
    if request.method == 'POST':
        try:
            # Charger les données JSON envoyées
            data = json.loads(request.body)
            # print(data)

            # Récupérer les données nécessaires
            activite_id = data.get('activite')
            article_id = data.get('articles')
            quantite = int(data.get('quantity'))

            # Validation des données
            if not activite_id or not article_id or quantite <= 0:
                return JsonResponse({'success': False, 'message': 'Données invalides.'})

            # Récupérer l'activité et l'article
            activite = Activite.objects.get(id=activite_id)
            article = Article.objects.get(id=article_id)

            # Calculer la quantité déjà réservée
            quantite_reservee = LigneReservation.objects.filter(article=article).aggregate(total=Sum('quantiteDemande'))['total'] or 0

            # Calculer la quantité restante
            quantite_restante = article.quantitedisponible - quantite_reservee

            # Vérifier la disponibilité de l'article
            if quantite_restante < quantite:
                return JsonResponse({
                    'success': False, 
                    'message': f"Quantité demandée pour l'article '{article.nom}' est supérieure à la quantité disponible. Quantité restante : {quantite_restante}"
                })

            # Créer une réservation
            reservation = Reservation.objects.create(
                nom=f"Réservation pour {activite.nom}",
                activite=activite,
                dateDebut=now()
            )

            # Créer une ligne de réservation
            ligne_reservation = LigneReservation.objects.create(
                reservation=reservation,
                article=article,
                quantiteDemande=quantite,
                dateDebut=now(),
                dateFin=now()
            )

            # Créer une notification de succès pour l'utilisateur qui a fait la réservation
            Notification.objects.create(
                destinataire=request.user,
                message=f"Votre réservation pour l'activité '{activite.nom}' a été effectuée avec succès.",
                lu=False 
            )

            return JsonResponse({'success': True, 'message': 'Réservation créée avec succès.'})
        
        except Activite.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Activité non trouvée.'})
        except Article.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Article non trouvé.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})



def get_activity(request, activity_id):
    try:
        activity = Activite.objects.get(id=activity_id)
        return JsonResponse({
            'id': activity.id,
            'nom': activity.nom,  # Utiliser 'nom' ici, comme défini dans votre modèle
            'sale': activity.sale,
            'dateDebut': activity.dateDebut.isoformat(), 
            'planning': activity.planning.id 
        })
    except Activite.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)


def deconnexion(request):
    logout(request)  # Déconnecte l'utilisateur
    return redirect('login')


def outils_count(request):
    count = Article.objects.count()
    return JsonResponse({"count": count})


@csrf_exempt
def modifier_ligne_reservation(request, ligne_reservation_id):
    
    """
    API pour modifier une ligne de réservation.
    Met à jour la quantité ou l'article associé.
    """
    
    if request.method == 'POST':
        try:
            # Charger les données JSON envoyées
            data = json.loads(request.body)
            quantite = int(data.get('quantite')) 
            article_id = data.get('articleId')

            # Validation des données
            if quantite <= 0 or not article_id:
                return JsonResponse({'success': False, 'message': 'Données invalides.'}, status=400)

            # Récupérer la ligne de réservation et l'article
            ligne_reservation = LigneReservation.objects.get(id=ligne_reservation_id)
            article = Article.objects.get(id=article_id)

            # Mise à jour de la ligne de réservation
            ligne_reservation.quantiteDemande = quantite
            ligne_reservation.article = article
            ligne_reservation.save()

            return JsonResponse({'success': True, 'message': 'Ligne de réservation mise à jour.'})

        except LigneReservation.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Ligne de réservation non trouvée.'}, status=404)
        except Article.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Article non trouvé.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'}, status=405)


@login_required
def delete_ligne_reservation(request, ligne_reservation_id):
    
    """
    Supprime une ligne de réservation en attente.
    """
    
    ligne_reservation = get_object_or_404(LigneReservation, id=ligne_reservation_id, reservation__statut='En attente') 

    if request.method == 'DELETE':
        ligne_reservation.delete()  # Supprimer la ligne de réservation
        return JsonResponse({'success': True}, status=200)

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)


# Vue pour afficher les notifications
def notification(request):
    
    """
    Charge les notifications non lues de l'utilisateur connecté.
    Affiche les notifications sur une page dédiée.
    """
    
    # Récupérer toutes les notifications non lues de l'utilisateur connecté
    notifications = Notification.objects.filter(destinataire=request.user, lu=False)
    context = {
        'notifications': notifications
    }
    return render(request, 'Atelier360/notifications.html', context)


# Vue API pour récupérer les notifications en JSON (pour le badge)
def get_notifications(request):

    """
    API pour récupérer les notifications non lues de l'utilisateur connecté.
    """

    notifications = Notification.objects.filter(destinataire=request.user, lu=False)
    notifications_data = [{
        'id': notification.id,
        'message': notification.message,
        'date': notification.date_envoi,
        'lu': notification.lu
    } for notification in notifications]

    return JsonResponse({'notifications': notifications_data})


# Vue pour marquer une notification comme lue
def mark_notification_as_read(request, notification_id):

    """
    Marque une notification comme lue.
    """

    try:
        notification = Notification.objects.get(id=notification_id, destinataire=request.user)
        notification.lu = True
        notification.save()
        return JsonResponse({'success': True, 'message': 'Notification marquée comme lue.'})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Notification non trouvée.'})
    