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

// Fonction pour récupérer les articles via une API
function getArticles() {
    // Appel API pour récupérer les articles
    fetch('/api/articles/')
        .then(response => response.json())
        .then(data => {
            console.log('Données récupérées:', data);

            const articlesSelect = document.getElementById('articles-select');
            if (!articlesSelect) {
                console.error('L\'élément #articles-select n\'a pas été trouvé.');
                return;
            }

            // Effacer les options existantes avant d'ajouter de nouvelles options
            articlesSelect.innerHTML = '';

            // Ajouter une option par défaut
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Sélectionner un article';
            articlesSelect.appendChild(defaultOption);

            // Ajouter les articles récupérés à la liste
            if (data.articles && Array.isArray(data.articles)) {
                data.articles.forEach(article => {
                    const option = document.createElement('option');
                    option.value = article.id;
                    option.textContent = article.nom;
                    articlesSelect.appendChild(option);
                });
            } else {
                console.error('Aucun article trouvé dans les données.');
                articlesSelect.innerHTML = '<option>Aucun article disponible.</option>';
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des articles:', error);
        });
}

// Fonction pour réserver une activité
function reserveActivity(activityId) {
    console.log("Réservation pour l'activité ID: " + activityId);

    // Appel API pour récupérer les détails de l'activité
    fetch(`/api/activities/${activityId}/`)
        .then(response => response.json())
        .then(activityData => {
            console.log('Données de l\'activité:', activityData);

            Swal.fire({
                title: 'Confirmer la réservation',
                html: `
                    <form id="reservation-form">
                        <label for="articles">Sélectionnez un article:</label>
                        <select id="articles-select" name="articles" class="form-control" required></select><br>
                        <label for="quantity">Quantité demandée:</label>
                        <input type="number" id="quantity" name="quantity" value="1" min="1" class="form-control" required>
                    </form>
                `,
                showCancelButton: true,
                confirmButtonText: 'Réserver',
                didOpen: () => {
                    console.log('Fenêtre modale ouverte');

                    // Charger les articles dans la fenêtre modale
                    getArticles();  // Charger les articles à l'ouverture du modal
                },
                preConfirm: () => {
                    const form = document.getElementById('reservation-form');
                    const formData = new FormData(form);
                    const selectedArticle = formData.get('articles');
                    console.log("efjkjpgf")
                    console.log(selectedArticle)
                    const quantity = formData.get('quantity');

                    console.log('Données envoyées à l\'API:', {
                        activity_id: activityId,
                        quantity: quantity,
                        articles: selectedArticle,
                        startDate: new Date().toISOString().split('T')[0], // Date au format YYYY-MM-DD
                    });

                    if (!selectedArticle || quantity <= 0) {
                        Swal.fire('Erreur', 'Veuillez remplir tous les champs.', 'error');
                        return false;
                    }

                    return {
                        activite: activityId,
                        articles: selectedArticle,
                        quantity: quantity,
                    };
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    const data = result.value;
                    fetch('/api/reservations/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        },
                        body: JSON.stringify(data),
                    })
                        .then(response => response.json())
                        .then(responseData => {
                            if (responseData.success) {
                                Swal.fire('Réservation confirmée!', '', 'success');
                            } else {
                                Swal.fire('Erreur', responseData.message, 'error');
                            }
                        })
                        .catch(error => {
                            console.error('Erreur lors de la réservation:', error);
                            Swal.fire('Erreur', 'La réservation a échoué.', 'error');
                        });
                }
            });
        })
        .catch(error => {
            console.error('Erreur:', error);
            Swal.fire('Erreur', 'Impossible de récupérer les informations.', 'error');
        });
}
