from django.contrib import admin
from .models import (
    Activite, Attribution, Categorie, Formateur,
    Inventaire, LigneAttribution, LigneInventaire,
    Planning, Reservation, ResponsableMetier, Utilisateur,
    Article, Departement, Metier, ChefDepartement, LigneReservation
)


class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'username', 'role', 'is_active', 'is_staff')
    search_fields = ('email', 'nom', 'prenom', 'username')

    fieldsets = (
        (None, {
            'fields': ('nom', 'prenom', 'email', 'matricule', 'role', 'username', 'password', 'is_active', 'is_staff', 'groups')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nom', 'prenom', 'email', 'matricule', 'role', 'username', 'password', 'is_active', 'is_staff', 'groups'),
        }),
    )

    ordering = ('nom',)

    def save_model(self, request, obj, form, change):
        if not change or 'password' in form.cleaned_data:
            obj.set_password(form.cleaned_data['password'])
        obj.save()


class ResponsableMetierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'dateDebut', 'dateFin')


class ActiviteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'dateDebut', 'salle')
    search_fields = ('nom', 'salle')
    ordering = ('dateDebut',)


# Enregistrement des modèles avec leur classe d'administration personnalisée
admin.site.register(ResponsableMetier, ResponsableMetierAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Activite, ActiviteAdmin)
admin.site.register(Attribution)
admin.site.register(Categorie)
admin.site.register(Departement)
admin.site.register(Metier)
admin.site.register(ChefDepartement)
admin.site.register(Formateur)
admin.site.register(Article)
admin.site.register(Inventaire)
admin.site.register(LigneAttribution)
admin.site.register(LigneInventaire)
admin.site.register(LigneReservation)
admin.site.register(Planning)
admin.site.register(Reservation)
