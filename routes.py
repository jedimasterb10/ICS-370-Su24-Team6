def setup_routes(app):
    from flask import request, jsonify, render_template, redirect, url_for
    from flask_login import login_user, logout_user, login_required, current_user
    from datetime import datetime, timedelta
    from smtplib import SMTP
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import threading

    from models import User, Appointment
    from app import db, login_manager

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
    @app.route('/register', methods=['POST'])
    def register():
        data = request.json
        user = User(
            name=data['name'],
            email=data['email'],
            notification_preferences=data.get('notification_preferences', '{"email": true, "sms": false}')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == ['POST']:
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
        return f"Hello, {current_user.name}! Welcome to your dashboard."

    @app.route('/book_appointment', methods=['POST'])
    @login_required
    def book_appointment():
        data = request.json
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

        return jsonify({'message': 'Appointment booked successfully'}), 201

    @app.route('/reschedule_appointment', methods=['POST'])
    @login_required
    def reschedule_appointment():
        data = request.json
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

        return jsonify({'message': 'Appointment rescheduled successfully'}), 200

    @app.route('/cancel_appointment', methods=['POST'])
    @login_required
    def cancel_appointment():
        data = request.json
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

        return jsonify({'message': 'Appointment canceled successfully'}), 200
