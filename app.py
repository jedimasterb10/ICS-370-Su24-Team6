from flask import Flask, request, redirect, url_for, render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User  # Local import to avoid circular import issues
    return User.query.get(int(user_id))

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

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        # Check if the email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already in use', 'error')
            return redirect(url_for('register'))

        # Create new user if email does not exist
        hashed_password = generate_password_hash(password)
        new_user = User(name=f"{first_name} {last_name}", email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

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
            return redirect(url_for('dashboard'))

        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    from models import Appointment  # Local import to avoid circular import issues
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    return render_template('dashboard.html', appointments=appointments)

@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@app.route('/get_appointments/<int:year>/<int:month>')
@login_required
def get_appointments(year, month):
    from models import Appointment  # Local import to avoid circular import issues
    
    start_date = date(year, month, 1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    appointments = Appointment.query.filter(Appointment.datetime >= start_date, Appointment.datetime <= end_date).all()

    appointments_by_day = {}
    for appt in appointments:
        day = appt.datetime.day
        if day not in appointments_by_day:
            appointments_by_day[day] = []
        appointments_by_day[day].append({
            'time': appt.datetime.strftime('%H:%M'),
            'patient': appt.patient_id,
            'id': appt.id
        })
    
    return jsonify(appointments_by_day)

@app.route('/day_view/<int:year>/<int:month>/<int:day>')
@login_required
def day_view(year, month, day):
    from models import Appointment  # Local import to avoid circular import issues
    
    selected_date = datetime(year, month, day)
    appointments = Appointment.query.filter(Appointment.datetime.date() == selected_date.date()).all()
    return render_template('day_view.html', appointments=appointments, selected_date=selected_date)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
