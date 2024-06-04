from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, login_user
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_migrate import Migrate
from datetime import date
from werkzeug.security import generate_password_hash
import os
from database import db
from create_roles import create_roles
from models import User, Role

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

    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    app.security = Security(app, user_datastore)

    with app.app_context():
        create_roles()

    return app
