# Atelier360/urls.py

from django.urls import path
from .views import user_login, home_view, page_view

urlpatterns = [
    path('', user_login, name='login'),
    path('home/', home_view, name='home'),
    path('page/', page_view, name='page'),
]
