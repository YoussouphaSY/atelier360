// Fonction pour obtenir le token CSRF
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

const csrftoken = getCookie('csrftoken');

// Fonction pour récupérer la liste des articles
document.addEventListener('DOMContentLoaded', function() {
    getArticles(); // Appelle la fonction dès que le DOM est complètement chargé
});

function getArticles() {
    const articlesSelect = document.getElementById('articles-select');

    // Vérifie si l'élément HTML existe
    if (!articlesSelect) {
        console.error('L\'élément #articles-select n\'a pas été trouvé.');
        return;
    }

    // Efface le contenu actuel
    articlesSelect.innerHTML = '';

    // Ajouter une option "Sélectionner" par défaut
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Sélectionner un article';
    articlesSelect.appendChild(defaultOption);

    // Appel API pour récupérer les articles
    fetch('/api/articles/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.articles && Array.isArray(data.articles)) {
                data.articles.forEach(article => {
                    const option = document.createElement('option');
                    option.value = article.id;
                    option.textContent = article.nom;
                    articlesSelect.appendChild(option);
                });
            } else {
                articlesSelect.innerHTML = '<option>Aucun article disponible.</option>';
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des articles:', error);
            articlesSelect.innerHTML = '<option>Erreur lors du chargement des articles.</option>';
        });
}

// Fonction pour réserver une activité
function reserveActivity(activityId) {
    console.log("Réservation pour l'activité ID: " + activityId); 

    // Appel API pour récupérer l'activité et ses dates
    fetch(`/api/activities/${activityId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(activityData => {
            // Vérifier si la date de début est présente
            if (!activityData.dateDebut) {
                Swal.fire('Erreur', 'La date de l\'activité est manquante.', 'error');
                return;
            }

            // Afficher un formulaire de réservation avec SweetAlert2
            Swal.fire({
                title: 'Confirmer la réservation',
                html: ` 
                    <form id="reservation-form">
                        <label for="articles">Sélectionnez un article:</label>
                        <select id="articles-select" name="articles" class="form-control" required></select><br>
                        
                        <label for="quantity">Quantité demandée:</label>
                        <input type="number" id="quantity" name="quantity" value="1" min="1" max="${activityData.quantityAvailable}" class="form-control" required>
                    </form>
                `,
                showCancelButton: true,
                confirmButtonText: 'Confirmer',
                cancelButtonText: 'Annuler',
                didOpen: () => {
                    // Appeler `getArticles` une fois que la modale est ouverte
                    getArticles();
                },
                preConfirm: () => {
                    const form = document.getElementById('reservation-form');
                    const formData = new FormData(form);

                    // Valider la sélection de l'article
                    const selectedArticle = formData.get('articles');
                    if (!selectedArticle) {
                        Swal.fire('Erreur', 'Veuillez sélectionner un article.', 'error');
                        return false;  // Bloque l'envoi si l'article n'est pas sélectionné
                    }

                    // Valider la quantité
                    const quantity = formData.get('quantity');
                    if (parseInt(quantity) <= 0) {
                        Swal.fire('Erreur', 'La quantité demandée doit être supérieure à zéro.', 'error');
                        return false;  // Bloque l'envoi si la quantité est invalide
                    }

                    // Retourner les données valides
                    return {
                        activity_id: activityId,
                        quantity: quantity,
                        articles: selectedArticle,
                        startDate: activityData.dateDebut 
                    };
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    const data = result.value;
                    console.log('Données envoyées à l\'API:', data);

                    if (data) {
                        // Envoi de la réservation au backend via l'API
                        fetch('/api/reservations/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrftoken,
                            },
                            body: JSON.stringify({
                                activite: data.activity_id,  // ID de l'activité
                                quantity: data.quantity,
                                articles: data.articles,
                                startDate: data.startDate,  // Date de début envoyée ici
                            })
                        })
                        .then(response => response.json())
                        .then(responseData => {
                            if (responseData.success) {
                                Swal.fire('Réservation confirmée!', '', 'success');
                            } else {
                                Swal.fire('Erreur', 'La réservation a échoué.', 'error');
                            }
                        })
                        .catch(error => {
                            console.error('Erreur lors de la réservation:', error);
                            Swal.fire('Erreur', 'La réservation a échoué.', 'error');
                        });
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des données de l\'activité:', error);
            Swal.fire('Erreur', 'Impossible de récupérer les informations de l\'activité.', 'error');
        });
}

