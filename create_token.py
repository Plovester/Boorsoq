from itsdangerous import URLSafeTimedSerializer


def generate_token(app, email):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])


def confirm_token(app, token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    try:
        email = serializer.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
        )
        return email
    except Exception:
        return False
