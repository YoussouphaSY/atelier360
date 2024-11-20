from django.urls import path

# Importation des vues et des vues API
from Atelier360.views_api import LigneReservationListCreateView
from .views import create_reservation, deconnexion, get_activity, get_articles, mes_reservations, notifications, planning, reserver, user_login, home_view, page_view, profil

urlpatterns = [
    # Page d'accueil pour l'utilisateur avec la vue de connexion
    path('', user_login, name='login'),

    # Page principale après la connexion (tableau de bord)
    path('home/', home_view, name='home'),

    # Page du profil de l'utilisateur
    path('profil/', profil, name='profil'),

    # Page supplémentaire (peut être utilisée pour des informations ou des configurations supplémentaires)
    path('page/', page_view, name='page'),

    # Route pour se déconnecter de l'application
    path('deconnexion/', deconnexion, name='deconnexion'),

    # Page pour afficher le planning des réservations (calendrier, etc.)
    path('planning/', planning, name='planning'),

    # Page pour afficher les notifications
    path('notifications/', notifications, name='notifications'),

    # API pour récupérer la liste des articles (utilisée par le frontend pour charger les articles disponibles)
    path('api/articles/', get_articles, name='get_articles'),

    # Page pour consulter les réservations de l'utilisateur
    path('mes_reservations/', mes_reservations, name='mes_reservations'),

    # API pour la gestion des réservations (liste et création via la classe `LigneReservationListCreateView`)
    path('api/mes_reservations/', LigneReservationListCreateView.as_view(), name='reservation-list'),

    # API pour créer une nouvelle réservation
    path('api/reservations/', create_reservation, name='create_reservation'),

    # Page permettant de faire une réservation (un système de sélection d'activite)
    path('reserver/', reserver, name='reserver'),

    # API pour récupérer les informations d'une activité spécifique
    path('api/activities/<int:activity_id>/', get_activity, name='get_activity'),
]
