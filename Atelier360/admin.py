from django.contrib import admin
from .models import (
    Activite, Attribution, Categorie, Formateur,
    Inventaire, LigneAttribution, LigneInventaire,
    Planning, Reservation, ResponsableMetier, Utilisateur,
    Article
)


class UtilisateurAdmin(admin.ModelAdmin):
    # Champs à afficher dans la liste des utilisateurs dans l'admin
    list_display = ('nom', 'prenom', 'email', 'username', 'role', "is_active")  # Ajout du champ username
    # Champs sur lesquels la recherche peut être effectuée
    search_fields = ('email', 'nom', 'prenom', 'username')  # Ajout de username dans la recherche

    # Configuration des champs à afficher dans le formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('nom', 'prenom', 'email', 'matricule', 'role', 'username', 'password', 'is_active')  # Ajout de username ici
        }),
    )

    # Configuration des champs à afficher lors de l'ajout d'un nouvel utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nom', 'prenom', 'email', 'matricule', 'role', 'username', 'password', 'is_active'),  # Ajout de username ici
        }),
    )

    # Ordre d'affichage des utilisateurs dans la liste
    ordering = ('nom',)  

    # Rendre le mot de passe modifiable dans le formulaire d'édition
    def save_model(self, request, obj, form, change):
        if not change:  # Si l'utilisateur est nouvellement créé
            obj.set_password(form.cleaned_data['password'])  # Hash le mot de passe
        obj.save()


class ActiviteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'dateDebut', 'salle')
    search_fields = ('nom', 'salle')
    ordering = ('dateDebut',)


# Enregistrement des modèles avec leur classe d'administration personnalisée
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Activite, ActiviteAdmin)
admin.site.register(Attribution)
admin.site.register(Categorie)
admin.site.register(Formateur)
admin.site.register(Article)
admin.site.register(Inventaire)
admin.site.register(LigneAttribution)
admin.site.register(LigneInventaire)
admin.site.register(Planning)
admin.site.register(Reservation)
admin.site.register(ResponsableMetier)
