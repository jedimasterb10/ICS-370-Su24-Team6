from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, Appointment

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        user = User(
            name=data['name'],
            email=data['email'],
            notification_preferences=data.get('notification_preferences', '{"email": true, "sms": false}')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)

@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        data = request.form
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=data['doctor_id'],
            datetime=datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S')
        )
        db.session.add(appointment)
        db.session.commit()

        if eval(current_user.notification_preferences).get('email'):
            subject = 'Appointment Confirmation'
            body = f"Dear {current_user.name},\n\nYour appointment is confirmed for {appointment.datetime}."
            send_email(current_user.email, subject, body)
            
            # Schedule reminder emails
            reminder_times = [appointment.datetime - timedelta(days=1), appointment.datetime - timedelta(hours=1)]
            for reminder_time in reminder_times:
                if reminder_time > datetime.now():
                    schedule_email(current_user.email, 'Appointment Reminder', body, reminder_time)

        return redirect(url_for('dashboard'))
    return render_template('book_appointment.html')

@app.route('/reschedule_appointment', methods=['GET', 'POST'])
@login_required
def reschedule_appointment():
    if request.method == 'POST':
        data = request.form
        appointment_id = data['appointment_id']
        new_datetime = datetime.strptime(data['new_datetime'], '%Y-%m-%d %H:%M:%S')

        appointment = Appointment.query.get(appointment_id)
        if appointment.patient_id != current_user.id:
            return jsonify({'message': 'Unauthorized'}), 403

        appointment.datetime = new_datetime
        appointment.status = 'rescheduled'
        db.session.commit()

        if eval(current_user.notification_preferences).get('email'):
            subject = 'Appointment Rescheduled'
            body = f"Dear {current_user.name},\n\nYour appointment has been rescheduled to {new_datetime}."
            send_email(current_user.email, subject, body)
            
            # Reschedule reminder emails
            reminder_times = [new_datetime - timedelta(days=1), new_datetime - timedelta(hours=1)]
            for reminder_time in reminder_times:
                if reminder_time > datetime.now():
                    schedule_email(current_user.email, 'Appointment Reminder', body, reminder_time)

        return redirect(url_for('dashboard'))
    return render_template('reschedule_appointment.html')

@app.route('/cancel_appointment', methods=['GET', 'POST'])
@login_required
def cancel_appointment():
    if request.method == 'POST':
        data = request.form
        appointment_id = data['appointment_id']

        appointment = Appointment.query.get(appointment_id)
        if appointment.patient_id != current_user.id:
            return jsonify({'message': 'Unauthorized'}), 403

        appointment.status = 'canceled'
        db.session.commit()

        if eval(current_user.notification_preferences).get('email'):
            subject = 'Appointment Canceled'
            body = f"Dear {current_user.name},\n\nYour appointment on {appointment.datetime} has been canceled."
            send_email(current_user.email, subject, body)

        return redirect(url_for('dashboard'))
    return render_template('cancel_appointment.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
