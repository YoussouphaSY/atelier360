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

fetch('/api/mes_reservations/')
    .then(response => response.json())
    .then(data => {
        console.log('Données récupérées:', data);  

        const tbody = document.getElementById('reservation-tbody');
        
        // Vérifier si 'reservations' est bien un tableau
        if (data && Array.isArray(data.reservations) && data.reservations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7">Aucune réservation trouvée.</td></tr>';
        } else if (data && Array.isArray(data.reservations)) {
            data.reservations.forEach(item => {
                const row = document.createElement('tr');
                
                // Ajoutez une condition pour afficher ou masquer les boutons selon le statut
                let actionButtons = '';
                if (item.statut === 'En attente') {
                    actionButtons = `
                        <button class="button-modifier btn-warning" onclick="editLigneReservation(${item.id}, ${item.quantite_demande}, ${item.article_id})">Modifier</button>
                        <button class="button-rouge" onclick="deleteLigneReservation(${item.id})">Supprimer</button>
                    `;
                }

                // Insérer les lignes de réservation et les informations
                item.lignes.forEach(ligne => {
                    row.innerHTML = `
                        <td>${item.activite_nom}</td>
                        <td>${item.activite_sale}</td>
                        <td>${ligne.article_nom}</td>
                        <td>${ligne.quantite_demande}</td>
                        <td>${ligne.quantite_validee}</td>  <!-- Affichage de la quantité validée -->
                        <td>${item.date_debut}</td>
                        <td>
                            <span class="badge ${item.statut === 'En attente' ? 'bg-warning' : item.statut === 'valide' ? 'bg-success' : 'bg-danger'}">
                                ${item.statut}
                            </span>
                        </td>
                        <td>${actionButtons}</td>
                    `;
                    tbody.appendChild(row);
                });
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="7">Données non valides reçues de l\'API.</td></tr>';
        }
    })
    .catch(error => {
        console.error('Erreur lors de la récupération des données', error);
    });

// Fonction pour éditer la ligne de réservation (modification de la quantité et de l'article)
function editLigneReservation(ligneReservationId, currentQuantity, currentArticleId) {
    // Appeler l'API pour récupérer les articles disponibles
    fetch('/api/articles/')
        .then(response => response.json())
        .then(data => {
            console.log('Réponse des articles:', data);  // Log de la réponse de l'API

            // Vérifier si l'API a bien renvoyé les articles sous forme de tableau
            if (Array.isArray(data.articles)) {
                let articlesOptions = '';
                data.articles.forEach(item => {
                    articlesOptions += `<option value="${item.id}" ${item.id === currentArticleId ? 'selected' : ''}>${item.nom}</option>`;
                });

                // Afficher la modale pour modifier la quantité et l'article
                Swal.fire({
                    title: 'Modifier la réservation',
                    html: `
                        <form id="edit-form">
                            <label for="article">Article :</label>
                            <select id="article" name="article" required class="swal2-input">
                                ${articlesOptions}
                            </select>
                            <br>
                            <label for="quantite">Quantité :</label>
                            <input type="number" id="quantite" name="quantite" value="${currentQuantity}" min="1" required class="swal2-input">
                        </form>
                    `,
                    showCancelButton: true,
                    confirmButtonText: 'Enregistrer',
                    cancelButtonText: 'Annuler',
                    preConfirm: () => {
                        const quantite = parseInt(document.getElementById('quantite').value);  // Convertir la quantité en entier
                        const articleId = document.getElementById('article').value;

                        // Vérifier si la quantité est valide
                        if (isNaN(quantite) || quantite <= 0) {
                            Swal.showValidationMessage('La quantité doit être un nombre positif.');
                            return false;
                        }

                        return {
                            ligneReservationId: ligneReservationId,
                            quantite: quantite,
                            articleId: articleId
                        };
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Log des données envoyées à l'API
                        console.log('Données envoyées à l\'API:', {
                            quantite: result.value.quantite,
                            articleId: result.value.articleId
                        });

                        // Envoi des données à l'API pour mettre à jour la ligne de réservation
                        fetch(`/api/modifier_ligne_reservation/${result.value.ligneReservationId}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')  // CSRF Token pour la sécurité
                            },
                            body: JSON.stringify({
                                quantite: result.value.quantite,
                                articleId: result.value.articleId
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Réponse de l\'API de modification:', data);  // Log de la réponse
                            if (data.success) {
                                Swal.fire('Modifié!', 'La réservation a été mise à jour.', 'success');
                                location.reload();  // Recharger la page pour voir les modifications
                            } else {
                                Swal.fire('Erreur', 'Il y a eu un problème lors de la modification.', 'error');
                            }
                        })
                        .catch(error => {
                            console.error('Erreur lors de la modification:', error);
                            Swal.fire('Erreur', 'Impossible de modifier la ligne de réservation.', 'error');
                        });
                    }
                });
            } else {
                // Si les articles ne sont pas disponibles sous forme de tableau
                Swal.fire('Erreur', 'Les articles ne sont pas disponibles.', 'error');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des articles:', error);
            Swal.fire('Erreur', 'Impossible de récupérer les articles disponibles.', 'error');
        });
}


// Fonction pour supprimer une ligne de réservation
function deleteLigneReservation(reservationId) {
    Swal.fire({
        title: 'Êtes-vous sûr de vouloir supprimer cette réservation ?',
        text: 'Cette action est irréversible.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Oui, supprimer!',
        cancelButtonText: 'Annuler'
    }).then((result) => {
        if (result.isConfirmed) {
            // Faire un appel API pour supprimer la réservation
            fetch(`/api/supprimer_ligne_reservation/${reservationId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')  // CSRF Token pour la sécurité
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('Supprimé!', 'La réservation a été supprimée.', 'success');
                    location.reload();  // Recharger la page pour voir la suppression
                } else {
                    Swal.fire('Erreur', 'Il y a eu un problème lors de la suppression.', 'error');
                }
            })
            .catch(error => {
                console.error('Erreur lors de la suppression:', error);
                Swal.fire('Erreur', 'Impossible de supprimer la réservation.', 'error');
            });
        }
    });
}
