from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, User


# Modèle Utilisateur avec les rôles définis
class Utilisateur(AbstractUser):
    ROLES = [
        ('admin', 'Administrateur'),
        ('metier', 'Responsable Métier'),
        ('formateur', 'Formateur'),
        ('gestionnaire', 'Gestionnaire'),
    ]

    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    matricule = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLES)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(Group, related_name="utilisateur_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="utilisateur_permissions")
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


# Modèle Formateur
class Formateur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, primary_key=True)
    specialisation = models.CharField(max_length=255)

    def __str__(self):
        return f"Formateur: {self.utilisateur.nom}"


# Modèle Responsable Métier
class ResponsableMetier(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, primary_key=True)  # Mettez à jour cette ligne
    dateDebut = models.DateField()
    dateFin = models.DateField()

    def __str__(self):
        return f"Responsable Métier: {self.utilisateur.nom}"


# Modèle Chef de Département
class ChefDepartement(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, primary_key=True)
    dateDebut = models.DateField()
    dateFin = models.DateField()

    def __str__(self):
        return f"Chef de Département: {self.utilisateur.nom}"


# Modèle Département
class Departement(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    chef = models.OneToOneField(ChefDepartement, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nom


# Modèle Métier
class Metier(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    formateurs = models.ManyToManyField(Formateur, related_name='metiers')
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='metiers')

    def __str__(self):
        return self.nom


# Modèle Planning
class Planning(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    dateDebut = models.DateField()
    dateFin = models.DateField()
    metier = models.ForeignKey(Metier, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


# Modèle Activité
class Activite(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    salle = models.CharField(max_length=255)
    dateDebut = models.DateField()
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name="activites")

    def __str__(self):
        return self.nom


# Modèle Réservation
class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    dateDebut = models.DateField(auto_now_add=True)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name="reservations")
    
    def __str__(self):
        return self.nom


# Modèle Catégorie
class Categorie(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.nom


# Modèle Article
class Article(models.Model):
    id = models.AutoField(primary_key=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    description = models.TextField()
    quantitedisponible = models.IntegerField()

    def __str__(self):
        return self.nom


# Modèle Inventaire
class Inventaire(models.Model):
    id = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=255)
    dateInventaire = models.DateField()

    def __str__(self):
        return self.libelle


# Modèle LigneInventaire
class LigneInventaire(models.Model):
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.IntegerField()

    def __str__(self):
        return f"{self.quantite} x {self.article.nom} in {self.inventaire.libelle}"


# Modèle LigneReservation
class LigneReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantiteDemande = models.IntegerField()
    quantiteValider = models.IntegerField()
    dateDebut = models.DateField()
    dateFin = models.DateField()
    # Pour les commentaires de validation
    commentaire = models.TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.quantiteDemande} x {self.article.nom} pour {self.reservation.nom}"


# Modèle Attribution
class Attribution(models.Model):
    id = models.AutoField(primary_key=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return f"Attribution of {self.article.nom} for {self.reservation.nom}"


# Modèle LigneAttribution
class LigneAttribution(models.Model):
    attribution = models.ForeignKey(Attribution, on_delete=models.CASCADE)
    quantite = models.IntegerField()

    def __str__(self):
        return f"{self.quantite} of {self.attribution.article.nom} in attribution"


# Modèle Notification pour tous les utilisateurs
class Notification(models.Model):
    """
    Modèle pour gérer les notifications des utilisateurs.
    """
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()  # Contenu de la notification
    date_envoi = models.DateTimeField(auto_now_add=True)  # Date et heure d'envoi
    lu = models.BooleanField(default=False)  # Statut de lecture de la notification

    def __str__(self):
        return f"Notification pour {self.destinataire.username}: {self.message[:30]}"

