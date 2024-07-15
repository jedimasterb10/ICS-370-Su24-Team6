import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///clinic_appointment.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', 'your_email@gmail.com')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your_email_password')
