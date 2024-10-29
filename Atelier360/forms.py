# Atelier360/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mot de passe", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
