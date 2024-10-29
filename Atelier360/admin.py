from django.contrib import admin
from .models import Activite, Attribution, Categorie, Compte, Equipement, Formateur, Gestionnaire, Inventaire, LigneAttribution, LigneInventaire, Notification, Planning, Reservation, ResponsableMetier, Utilisateur


class UtilisateurAdmin(admin.ModelAdmin):
    # Champs à afficher dans la liste des utilisateurs dans l'admin
    list_display = ('username', 'email', 'role')  
    # Champs sur lesquels la recherche peut être effectuée
    search_fields = ('username', 'email')  

    # Configuration des champs à afficher dans le formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password', 'role')  # Champs à afficher dans le formulaire
        }),
    )

    # Configuration des champs à afficher lors de l'ajout d'un nouvel utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'role'),  # Champs lors de l'ajout
        }),
    )

    # Ordre d'affichage des utilisateurs dans la liste
    ordering = ('username',)  

    # Rendre le mot de passe modifiable dans le formulaire d'édition
    def save_model(self, request, obj, form, change):
        if not change:  # Si l'utilisateur est nouvellement créé
            obj.set_password(form.cleaned_data['password'])  # Hash le mot de passe
        obj.save()


class ActiviteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date', 'description')
    search_fields = ('nom', 'description')
    ordering = ('date',)


# Enregistrement du modèle Utilisateur avec sa classe d'administration personnalisée
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Activite, ActiviteAdmin)
admin.site.register(Attribution)
admin.site.register(Categorie)
admin.site.register(Compte)
admin.site.register(Equipement)
admin.site.register(Formateur)
admin.site.register(Gestionnaire)
admin.site.register(Inventaire)
admin.site.register(LigneAttribution)
admin.site.register(LigneInventaire)
admin.site.register(Notification)
admin.site.register(Planning)
admin.site.register(Reservation)
admin.site.register(ResponsableMetier)
