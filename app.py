from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Local imports
from config import config

# Initialize Flask app and configurations
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Local import to avoid circular import issues
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        from models import User  # Local import to avoid circular import issues
        
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=hashed_password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login', role=role))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        from models import User  # Local import to avoid circular import issues
        
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Login successful! Welcome, {user.first_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')

        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    appointments = current_user.appointments
    return render_template('dashboard.html', appointments=appointments)

@app.route('/calendar')
@login_required
def calendar_view():
    # Calendar logic here
    return render_template('calendar.html')

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    from models import Appointment  # Local import to avoid circular import issues
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        new_appointment = Appointment(date=date, time=time, status='Scheduled', patient_id=current_user.id)
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('book_appointment.html')

@app.route('/reschedule/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def reschedule_appointment(appointment_id):
    from models import Appointment  # Local import to avoid circular import issues
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        appointment.date = request.form['date']
        appointment.time = request.form['time']
        db.session.commit()
        flash('Appointment rescheduled successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('reschedule_appointment.html', appointment=appointment)

@app.route('/cancel/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    from models import Appointment  # Local import to avoid circular import issues
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment canceled successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def update_notification_settings():
    if request.method == 'POST':
        notification_method = request.form['notification_method']
        notification_intervals = request.form['notification_intervals']
        
        current_user.notification_method = notification_method
        current_user.notification_intervals = notification_intervals
        db.session.commit()
        flash('Notification settings updated successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('settings.html', user=current_user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
