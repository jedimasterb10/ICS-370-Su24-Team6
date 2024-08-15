from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Administrator(db.Model, UserMixin):
    __tablename__ = 'administrators'
    adminID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Staff(db.Model, UserMixin):
    __tablename__ = 'staff'
    staffID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)

    adminID = db.Column(db.Integer, db.ForeignKey('administrators.adminID'))
    admin = db.relationship('Administrator', backref='staff')


class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctorID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

    adminID = db.Column(db.Integer, db.ForeignKey('administrators.adminID'))
    admin = db.relationship('Administrator', backref='doctors')


class Patient(db.Model):
    __tablename__ = 'patients'
    patientID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)

    appointments = db.relationship('Appointment', backref='patient', lazy=True)


class Availability(db.Model):
    __tablename__ = 'availabilities'
    availabilityID = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    startTime = db.Column(db.Time, nullable=False)
    endTime = db.Column(db.Time, nullable=False)

    doctorID = db.Column(db.Integer, db.ForeignKey('doctors.doctorID'))
    doctor = db.relationship('Doctor', backref='availabilities')


class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointmentID = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), nullable=False)

    patientID = db.Column(db.Integer, db.ForeignKey('patients.patientID'))
    availabilityID = db.Column(db.Integer, db.ForeignKey('availabilities.availabilityID'))

    notifications = db.relationship('Notification', backref='appointment', lazy=True)


class Notification(db.Model):
    __tablename__ = 'notifications'
    notificationID = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    dateSent = db.Column(db.DateTime, nullable=False)

    appointmentID = db.Column(db.Integer, db.ForeignKey('appointments.appointmentID'))
