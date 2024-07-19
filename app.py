from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize plugins
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from models import User, Appointment
        db.create_all()

    from routes import setup_routes
    setup_routes(app)  # Pass the app instance to the setup_routes function

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
