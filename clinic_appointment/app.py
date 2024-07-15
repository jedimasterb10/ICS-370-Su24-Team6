from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

from models import User, Appointment

# Utility functions
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = app.config['EMAIL_USERNAME']
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with SMTP(app.config['EMAIL_HOST'], app.config['EMAIL_PORT']) as server:
        server.starttls()
        server.login(app.config['EMAIL_USERNAME'], app.config['EMAIL_PASSWORD'])
        server.send_message(msg)

def schedule_email(to_email, subject, body, send_time):
    delay = (send_time - datetime.now()).total_seconds()
    threading.Timer(delay, send_email, args=[to_email, subject, body]).start()

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],  # Password should be hashed in production
        notification_preferences=data.get('notification_preferences', {'email': True, 'sms': False})
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    data = request.json
    appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        datetime=datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S')
    )
    db.session.add(appointment)
    db.session.commit()

    patient = User.query.get(appointment.patient_id)
    if patient and patient.notification_preferences.get('email'):
        subject = 'Appointment Confirmation'
        body = f"Dear {patient.name},\n\nYour appointment is confirmed for {appointment.datetime}."
        send_email(patient.email, subject, body)
        
        # Schedule reminder emails
        reminder_times = [appointment.datetime - timedelta(days=1), appointment.datetime - timedelta(hours=1)]
        for reminder_time in reminder_times:
            if reminder_time > datetime.now():
                schedule_email(patient.email, 'Appointment Reminder', body, reminder_time)

    return jsonify({'message': 'Appointment booked successfully'}), 201

@app.route('/reschedule_appointment', methods=['POST'])
def reschedule_appointment():
    data = request.json
    appointment_id = data['appointment_id']
    new_datetime = datetime.strptime(data['new_datetime'], '%Y-%m-%d %H:%M:%S')

    appointment = Appointment.query.get(appointment_id)
    appointment.datetime = new_datetime
    appointment.status = 'rescheduled'
    db.session.commit()

    patient = User.query.get(appointment.patient_id)
    if patient and patient.notification_preferences.get('email'):
        subject = 'Appointment Rescheduled'
        body = f"Dear {patient.name},\n\nYour appointment has been rescheduled to {new_datetime}."
        send_email(patient.email, subject, body)
        
        # Reschedule reminder emails
        reminder_times = [new_datetime - timedelta(days=1), new_datetime - timedelta(hours=1)]
        for reminder_time in reminder_times:
            if reminder_time > datetime.now():
                schedule_email(patient.email, 'Appointment Reminder', body, reminder_time)

    return jsonify({'message': 'Appointment rescheduled successfully'}), 200

@app.route('/cancel_appointment', methods=['POST'])
def cancel_appointment():
    data = request.json
    appointment_id = data['appointment_id']

    appointment = Appointment.query.get(appointment_id)
    appointment.status = 'canceled'
    db.session.commit()

    patient = User.query.get(appointment.patient_id)
    if patient and patient.notification_preferences.get('email'):
        subject = 'Appointment Canceled'
        body = f"Dear {patient.name},\n\nYour appointment on {appointment.datetime} has been canceled."
        send_email(patient.email, subject, body)

    return jsonify({'message': 'Appointment canceled successfully'}), 200

if __name__ == '__main__':
    from models import db
    db.init_app(app)
    app.run(debug=True)
