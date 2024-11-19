// Appeler l'API pour récupérer les lignes de réservation de l'utilisateur connecté
fetch('/api/mes_reservations/')
    .then(response => response.json())
    .then(data => {
        const tbody = document.getElementById('reservation-tbody');
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3">Aucune réservation trouvée.</td></tr>';
        } else {
            data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.reservation.activite.nom}</td>
                    <td>${item.reservation.activite.salle}</td>
                    <td>${item.article.nom}</td>
                    <td>${item.quantiteDemande}</td>
                    <td>${item.reservation.dateDebut}</td>
                `;
                tbody.appendChild(row);
            });
        }
    })
    .catch(error => {
        console.error('Erreur lors de la récupération des données', error);
    });
