from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from database import db
from create_roles import create_roles
from create_admin import create_admin

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

    with (app.app_context()):
        create_roles()
        create_admin()

    return app
