function addReservation() {
    // Récupérer les valeurs du formulaire
    const equipment = document.getElementById("equipment").value;
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;
    const reason = document.getElementById("reason").value;

    // Vérifier que tous les champs sont remplis
    if (equipment && date && time && reason) {
        // Créer une nouvelle ligne pour le tableau
        const tableBody = document.getElementById("equipment-list-body");
        const newRow = document.createElement("tr");

        // Créer des cellules pour l'équipement, la date, l'heure et le motif
        const equipmentCell = document.createElement("td");
        equipmentCell.textContent = equipment;
        newRow.appendChild(equipmentCell);

        const dateCell = document.createElement("td");
        dateCell.textContent = date;
        newRow.appendChild(dateCell);

        const timeCell = document.createElement("td");
        timeCell.textContent = time;
        newRow.appendChild(timeCell);

        const reasonCell = document.createElement("td");
        reasonCell.textContent = reason;
        newRow.appendChild(reasonCell);

        // Ajouter la nouvelle ligne au tableau
        tableBody.appendChild(newRow);

        // Réinitialiser le formulaire après ajout
        document.getElementById("reservation-form").reset();
    } else {
        alert("Veuillez remplir tous les champs !");
    }
}
