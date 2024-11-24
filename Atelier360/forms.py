from django import forms
from django.contrib.auth.forms import AuthenticationForm

from Atelier360.models import LigneReservation


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class LigneReservationForm(forms.ModelForm):
    class Meta:
        model = LigneReservation
        fields = ['quantiteDemande']  # Vous pouvez ajouter d'autres champs que vous souhaitez rendre modifiables
        widgets = {
            'quantiteDemande': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_quantiteDemande(self):
        quantite = self.cleaned_data.get('quantiteDemande')
        if quantite <= 0:
            raise forms.ValidationError("La quantité doit être un nombre positif.")
        return quantite