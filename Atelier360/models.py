from django.db import models
from django.contrib.auth.models import AbstractUser

# Modèles Utilisateurs


class Utilisateur(AbstractUser):
    ROLES = [
        ('admin', 'Administrateur'),
        ('metier', 'Responsable Métier'),
        ('formateur', 'Formateur'),
        ('gestionnaire', 'Gestionnaire'),
    ]
    role = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class Formateur(Utilisateur):
    pass


class ResponsableMetier(Utilisateur):
    specialite = models.CharField(max_length=100)


class Gestionnaire(Utilisateur):
    pass


# Catégorie et Équipement
class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Equipement(models.Model):
    nom = models.CharField(max_length=100)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    etat = models.CharField(max_length=50, choices=[('fonctionnel', 'Fonctionnel'), ('reparation', 'En réparation'), ('hors_service', 'Hors service')])

    def __str__(self):
        return f"{self.nom} ({self.categorie})"


# Modèles de Réservation et de Planning #

class Reservation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=[('en_attente', 'En attente'), ('approuve', 'Approuvé'), ('refuse', 'Refusé')])

    def __str__(self):
        return f"Réservation {self.id} - {self.equipement} par {self.utilisateur}"


class Planning(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    activites = models.ManyToManyField('Activite', through='Attribution')

    def __str__(self):
        return f"Planning de {self.utilisateur} du {self.date_debut} au {self.date_fin}"


class Activite(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.nom


class Attribution(models.Model):
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    responsable = models.ForeignKey(ResponsableMetier, on_delete=models.CASCADE)

    def __str__(self):
        return f"Attribution {self.activite} dans {self.planning}"


class LigneAttribution(models.Model):
    attribution = models.ForeignKey(Attribution, on_delete=models.CASCADE)
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantite} x {self.equipement} pour {self.attribution}"


# Gestion des Stocks et Inventaire ###

class Inventaire(models.Model):
    responsable = models.ForeignKey(Gestionnaire, on_delete=models.CASCADE)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inventaire mis à jour par {self.responsable} le {self.date_mise_a_jour}"


class LigneInventaire(models.Model):
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE)
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    quantite_disponible = models.PositiveIntegerField()
    seuil_alerte = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite_disponible} x {self.equipement} dans l'inventaire"


# Notifications

class Notification(models.Model):
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    message = models.TextField()
    date_envoye = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification pour {self.destinataire} - {'Lu' if self.lu else 'Non lu'}"


# Comptes et Authentification

class Compte(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compte de {self.utilisateur}"
