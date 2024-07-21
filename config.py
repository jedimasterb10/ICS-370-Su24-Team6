class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///appointments.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EMAIL_HOST = 'smtp.example.com'
    EMAIL_PORT = 587
    EMAIL_USERNAME = 'your_email@example.com'
    EMAIL_PASSWORD = 'your_email_password'
