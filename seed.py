from create_roles import create_roles
from create_admin import create_admin
from app import create_app

if __name__ == '__main__':
    app = create_app()

    with (app.app_context()):
        create_roles()
        create_admin()
