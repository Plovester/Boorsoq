from models import Role
from database import db


ROLE_NAMES = ["Admin", "User"]


def create_roles():
    for role_name in ROLE_NAMES:
        role = Role.query.filter_by(name=role_name).first()

        if not role:
            db.session.add(Role(name=role_name))
            db.session.commit()
