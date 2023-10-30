from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
import os

app = Flask(__name__)
Bootstrap5(app)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()

    if request.method == 'POST':
        user = User.query.filter_by(email=register_form.email.data).first()

        if not user:
            if register_form.validate_on_submit():
                hashed_password = generate_password_hash(register_form.password.data, method='pbkdf2:sha256', salt_length=8)

                new_user = User(
                    name=register_form.name.data,
                    email=register_form.email.data,
                    password=hashed_password
                )

                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)

                return redirect(url_for('home'))
        else:
            flash('The email has already exist. Try to log in')
            return redirect(url_for('login'))
    return render_template("register.html", form=register_form)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()

    if request.method == 'POST':
        if login_form.validate_on_submit():
            user = User.query.filter_by(email=request.form.get('email')).first()

            if user:
                user_password = user.password
                password = login_form.password.data
                is_password_correct = check_password_hash(user_password, password)

                if is_password_correct:
                    login_user(user)
                    return redirect(url_for('home'))
                else:
                    flash('Your password is not correct. Try again')
                    return redirect(url_for('login'))
            else:
                flash('The email does not exist. Try again or register')
                return redirect('login')

    return render_template("register.html", form=login_form)


if __name__ == "__main__":
    app.run(debug=True)
