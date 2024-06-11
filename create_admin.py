from werkzeug.security import generate_password_hash
from models import Role, User
from database import db


def create_admin():
    admin_role = Role.query.filter_by(name='Admin').first()

    if len(admin_role.users) == 0:
        hashed_password = generate_password_hash('admin', method='pbkdf2:sha256', salt_length=8)

        first_admin = User(
            name='admin',
            phone_number='111111',
            email='admin',
            password=hashed_password
        )

        first_admin.roles.append(admin_role)

        db.session.add(first_admin)
        db.session.commit()


