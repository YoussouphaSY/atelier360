// Récupérer le nombre de notifications non lues
function updateNotificationBadge() {
    fetch('/api/get_notifications/')
        .then(response => response.json())
        .then(data => {
            // Mettre à jour le badge de notification avec le nombre de notifications non lues
            const notificationCount = data.notifications.length;
            const notificationBadge = document.getElementById('notification-badge');
            
            if (notificationBadge) {
                if (notificationCount > 0) {
                    notificationBadge.textContent = notificationCount;  // Afficher le nombre de notifications
                    notificationBadge.style.display = 'inline';  // Assurez-vous que le badge est visible
                } else {
                    notificationBadge.style.display = 'none';  // Masquer le badge si aucune notification
                }
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des notifications:', error);
        });
}

// Appeler cette fonction au chargement de la page
window.onload = function() {
    updateNotificationBadge();
};


function markAsRead(notificationId) {
    // Appel API pour marquer la notification comme lue
    fetch(`/api/mark_notification_as_read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // CSRF Token pour la sécurité
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Vérifiez si l'élément existe avant de le manipuler
            const notificationItem = document.getElementById(`notification-${notificationId}`);
            if (notificationItem) {
                notificationItem.classList.remove('unread'); // Retirer la classe 'unread' pour marquer comme lue
                Swal.fire('Notification marquée comme lue!', '', 'success');
            } else {
                console.error('Notification non trouvée dans le DOM');
            }
        } else {
            Swal.fire('Erreur', data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Erreur lors de la mise à jour de la notification:', error);
        Swal.fire('Erreur', 'Impossible de marquer la notification comme lue.', 'error');
    });
}


// Fonction pour obtenir le cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
