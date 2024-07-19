// scripts.js

// Function to show the calendar for a given month and year
function showCalendar(month, year) {
    const monthYearElement = document.getElementById('month-year');
    monthYearElement.textContent = `${month} ${year}`;
    
    const calendarGrid = document.querySelector('.calendar-grid');
    calendarGrid.innerHTML = ''; // Clear previous content
    
    // Add day names
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayNames.forEach(name => {
        const dayNameElement = document.createElement('div');
        dayNameElement.className = 'day-name';
        dayNameElement.textContent = name;
        calendarGrid.appendChild(dayNameElement);
    });
    
    // Get the first day of the month and the number of days in the month
    const firstDay = new Date(year, monthToNumber(month), 1).getDay();
    const lastDate = new Date(year, monthToNumber(month) + 1, 0).getDate();
    
    // Add empty divs for the days before the first day
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day empty';
        calendarGrid.appendChild(emptyDay);
    }
    
    // Add days of the month
    for (let i = 1; i <= lastDate; i++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        dayElement.dataset.date = `${year}-${monthToNumber(month) + 1}-${i}`;
        dayElement.innerHTML = `<span class="day-number">${i}</span><span class="appointment-count">0</span>`;
        
        dayElement.addEventListener('click', function() {
            showAppointmentDetails(dayElement.dataset.date);
        });
        
        calendarGrid.appendChild(dayElement);
    }
}

// Function to convert month name to month number (0-based index)
function monthToNumber(month) {
    return new Date(Date.parse(month +" 1, 2012")).getMonth();
}

// Function to show appointment details in a popup
function showAppointmentDetails(date) {
    // Example data - replace with actual appointment data retrieval
    const appointments = [
        { time: '10:00 AM', doctor: 'Dr. Smith', patient: 'John Doe' },
        { time: '11:00 AM', doctor: 'Dr. Jones', patient: 'Jane Doe' }
    ];
    
    const popup = document.getElementById('appointment-popup');
    const popupDate = document.getElementById('popup-date');
    const appointmentList = document.getElementById('appointment-list');
    
    popupDate.textContent = date;
    appointmentList.innerHTML = ''; // Clear previous content
    
    appointments.forEach(appointment => {
        const appointmentItem = document.createElement('li');
        appointmentItem.innerHTML = `
            <p><strong>${appointment.doctor}</strong> - ${appointment.time} with ${appointment.patient}</p>
            <button class="action-button">Reschedule</button>
            <button class="action-button">Cancel</button>
        `;
        appointmentList.appendChild(appointmentItem);
    });
    
    popup.style.display = 'flex';
}

// Function to handle month navigation
function changeMonth(direction) {
    const monthYearElement = document.getElementById('month-year');
    const [currentMonth, currentYear] = monthYearElement.textContent.split(' ');
    
    let monthIndex = monthToNumber(currentMonth);
    let year = parseInt(currentYear);
    
    if (direction === 'next') {
        monthIndex++;
        if (monthIndex > 11) {
            monthIndex = 0;
            year++;
        }
    } else if (direction === 'prev') {
        monthIndex--;
        if (monthIndex < 0) {
            monthIndex = 11;
            year--;
        }
    }
    
    showCalendar(numberToMonth(monthIndex), year);
}

// Function to convert month index to month name
function numberToMonth(index) {
    return new Date(0, index).toLocaleString('en', { month: 'long' });
}

// Event listeners for month navigation buttons
document.getElementById('prev-month').addEventListener('click', function() {
    changeMonth('prev');
});

document.getElementById('next-month').addEventListener('click', function() {
    changeMonth('next');
});

// Close popup when clicking on close button
document.querySelector('.close-popup').addEventListener('click', function() {
    document.getElementById('appointment-popup').style.display = 'none';
});

// Initialize calendar for the current month and year
const today = new Date();
showCalendar(numberToMonth(today.getMonth()), today.getFullYear());
