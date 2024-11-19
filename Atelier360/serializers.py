from rest_framework import serializers
from .models import Categorie, Reservation, LigneReservation, Article, Activite


class ActiviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activite
        fields = ['id', 'nom', 'salle', 'dateDebut'] 



class ReservationSerializer(serializers.ModelSerializer):
    activite = ActiviteSerializer()

    class Meta:
        model = Reservation
        fields = ['id', 'nom', 'dateDebut', 'activite']
        

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description']


# Sérialiseur pour le modèle Article
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'nom', 'description', 'categorie']
        

class LigneReservationSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)  # Affiche le nom de l'outil réservé
    reservation = ReservationSerializer(read_only=True)  # Lien vers la réservation, un seul objet

    class Meta:
        model = LigneReservation
        fields = ['id', 'article', 'quantiteDemande', 'quantiteValider', 'dateDebut', 'dateFin', 'commentaire', 'reservation']
        

