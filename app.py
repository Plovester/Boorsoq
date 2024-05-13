from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import date
from werkzeug.security import generate_password_hash
import os

from database import db
from models import Admin

migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    Bootstrap5(app)

    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

    login_manager.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        admin = Admin.query.filter_by(email='admin').first()
        hashed_password = generate_password_hash('admin', method='pbkdf2:sha256', salt_length=8)

        if not admin:
            first_admin = Admin(
                name='admin',
                email='admin',
                password=hashed_password,
                created_at=date.today()
            )

            db.session.add(first_admin)
            db.session.commit()

    return app
