# Atelier360/backends.py

from django.contrib.auth.backends import ModelBackend
from .models import Utilisateur


class MatriculeBackend(ModelBackend):
    def authenticate(self, request, matricule=None, password=None, **kwargs):
        try:
            user = Utilisateur.objects.get(matricule=matricule)
        except Utilisateur.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
