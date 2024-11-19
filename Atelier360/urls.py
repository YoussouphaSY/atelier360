# Atelier360/urls.py

from django.urls import path

from Atelier360.views_api import LigneReservationListCreateView
from .views import  add_reservation_detail, create_reservation, deconnexion, get_activity, get_articles, mes_reservations, notifications, planning, user_login, home_view, page_view, profil


urlpatterns = [
    path('', user_login, name='login'),
    path('home/', home_view, name='home'),
    path('profil/', profil, name='profil'),
    path('page/', page_view, name='page'),

    path('deconnexion/', deconnexion, name='deconnexion'),
 
    path('planning/', planning, name='planning'),
    path('notifications/', notifications, name='notifications'),


    path('api/articles/', get_articles, name='get_articles'),

    path('mes_reservations/', mes_reservations, name='mes_reservations'),
    
    path('api/mes_reservations/', LigneReservationListCreateView.as_view(), name='reservation-list'),
    

    path('api/reservations/', create_reservation, name='create_reservation'),
    path('api/reservation-details/', add_reservation_detail, name='add_reservation_detail'),
    path('api/activities/<int:activity_id>/', get_activity, name='get_activity'),


]
