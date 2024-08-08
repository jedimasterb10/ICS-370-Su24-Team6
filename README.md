# ICS-370-Su24-Team6

This is the repository for Team 6's project for the Summer 2024 session of ICS 370: Software Design Models at Metropolitan State University.

Collaborators: Benjamin O'Konski, Aidurus Ibrahim, Tsion Sisay, Othello Metzger

Project: Medical office appointment scheduling system with automated notifications

Current file map:
```
ICS-370-Su24-Team6/
│
├── app.py                           # Main Flask application file
├── config.py                        # Configuration settings for Flask and SQLAlchemy
├── models.py                        # SQLAlchemy models
│
├── templates/                       # HTML template files
│   ├── base.html                    # Base template with common layout elements
│   ├── home.html                    # Home page with options to register or log in
│   ├── dashboard.html               # Dashboard page for logged-in users
│   ├── book_appointment.html        # Appointment booking page
│   ├── reschedule_appointment.html  # Appointment rescheduling page
│   ├── cancel_appointment.html      # Appointment cancellation page
│   ├── login.html                   # Login page
│   ├── register.html                # Registration page
│   └── calendar.html                # Calendar view displaying appointments
│
├── static/                          # Static files (e.g., CSS, JavaScript)
│   ├── css/
│   │   └── styles.css               # CSS file for styling
│   ├── js/
│   │   └── scripts.js               # JavaScript file for client-side logic
│
└── requirements.txt                 # File listing project dependencies
```
