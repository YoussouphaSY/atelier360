def notifier_formateur(reservation):
    from .models import Notification 

    # Récupérer le formateur lié à l'activité de la réservation
    try:
        formateur = reservation.activite.planning.metier.formateurs.first().utilisateur
        message = f"L'article '{reservation.attribution.article.nom}' a été attribué à votre réservation '{reservation.nom}'."

        # Créer une notification pour le formateur
        Notification.objects.create(destinataire=formateur, message=message)
    except AttributeError:
        # Gérer les cas où le formateur ou les relations sont manquants
        print("Impossible de notifier le formateur. Vérifiez les relations entre les modèles.")
