from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize database
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models
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
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        return 'Invalid email or password'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        datetime_str = request.form['datetime']
        appointment_datetime = datetime.fromisoformat(datetime_str)
        new_appointment = Appointment(patient_id=current_user.id, doctor_id=doctor_id, datetime=appointment_datetime)
        db.session.add(new_appointment)
        db.session.commit()

        # Send confirmation email
        subject = 'Appointment Confirmed'
        body = f'Your appointment with Doctor {doctor_id} is scheduled for {appointment_datetime}.'
        schedule_email(current_user.email, subject, body, appointment_datetime - timedelta(hours=1))

        return redirect(url_for('dashboard'))
    return render_template('book_appointment.html')

@app.route('/reschedule', methods=['GET', 'POST'])
@login_required
def reschedule_appointment():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        new_datetime_str = request.form['new_datetime']
        new_datetime = datetime.fromisoformat(new_datetime_str)

        appointment = Appointment.query.get(appointment_id)
        if appointment and appointment.patient_id == current_user.id:
            appointment.datetime = new_datetime
            db.session.commit()

            # Send updated confirmation email
            subject = 'Appointment Rescheduled'
            body = f'Your appointment with Doctor {appointment.doctor_id} has been rescheduled to {new_datetime}.'
            schedule_email(current_user.email, subject, body, new_datetime - timedelta(hours=1))

        return redirect(url_for('dashboard'))
    return render_template('reschedule_appointment.html')

@app.route('/cancel', methods=['GET', 'POST'])
@login_required
def cancel_appointment():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        appointment = Appointment.query.get(appointment_id)
        if appointment and appointment.patient_id == current_user.id:
            db.session.delete(appointment)
            db.session.commit()

            # Send cancellation email
            subject = 'Appointment Canceled'
            body = f'Your appointment with Doctor {appointment.doctor_id} has been canceled.'
            send_email(current_user.email, subject, body)

        return redirect(url_for('dashboard'))
    return render_template('cancel_appointment.html')

if __name__ == '__main__':
    app.run(debug=True)
