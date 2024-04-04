from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import date
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

        if not admin:
            first_admin = Admin(
                name='admin',
                email='admin',
                password='admin',
                created_at=date.today()
            )

            db.session.add(first_admin)
            db.session.commit()

    return app
