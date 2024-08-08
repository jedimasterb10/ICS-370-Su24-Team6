document.addEventListener('DOMContentLoaded', function() {
    const calendarCells = document.querySelectorAll('.calendar-cell');
    const appointmentDetailsPopup = document.getElementById('appointmentDetailsPopup');
    const closePopupButton = document.getElementById('closePopupButton');

    calendarCells.forEach(cell => {
        cell.addEventListener('click', function() {
            const appointments = this.dataset.appointments;
            if (appointments) {
                document.getElementById('appointmentList').innerHTML = appointments;
                appointmentDetailsPopup.style.display = 'block';
            }
        });
    });

    closePopupButton.addEventListener('click', function() {
        appointmentDetailsPopup.style.display = 'none';
    });
});
