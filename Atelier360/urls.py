from django.urls import path

# Importation des vues et des vues API
from Atelier360.views_api import LigneReservationListCreateView
from .views import create_reservation, deconnexion, delete_ligne_reservation, get_activity, get_articles, get_notifications, mark_notification_as_read, mes_reservations, modifier_ligne_reservation, notification, outils_count, planning, user_login, home_view, page_view, profil

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
    path('notifications/', notification, name='notifications'),  # Page utilisateur

    # API pour récupérer la liste des articles (utilisée par le frontend pour charger les articles disponibles)
    path('api/articles/', get_articles, name='get_articles'),

    # Page pour consulter les réservations de l'utilisateur
    path('mes_reservations/', mes_reservations, name='mes_reservations'),

    # API pour la gestion des réservations (liste et création via la classe `LigneReservationListCreateView`)
    path('api/mes_reservations/', LigneReservationListCreateView.as_view(), name='reservation-list'),

    # API pour créer une nouvelle réservation
    path('api/reservations/', create_reservation, name='create_reservation'),

    # API pour récupérer les informations d'une activité spécifique
    path('api/activities/<int:activity_id>/', get_activity, name='get_activity'),

    # API pour compter les outils disponibles
    path("admin/outils-count/", outils_count, name="outils_count"),

    # Route pour modifier une ligne de réservation
    path('api/modifier_ligne_reservation/<int:ligne_reservation_id>/', modifier_ligne_reservation, name='modify_ligne_reservation'),

    # Route pour supprimer une ligne de réservation via API
    path('api/supprimer_ligne_reservation/<int:ligne_reservation_id>/', delete_ligne_reservation, name='delete_ligne_reservation'),

    # API pour recuperer les notifications 
    path('api/get_notifications/', get_notifications, name='notify'),

    # API pour marquer notification comme lu
    path('api/mark_notification_as_read/<int:notification_id>/', mark_notification_as_read, name='mark-notification-as-read'),
    
]
