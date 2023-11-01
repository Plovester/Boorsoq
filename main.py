from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, AddNewItemForm
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


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()

    if not current_user.is_authenticated:
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

    if not current_user.is_authenticated:
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    result = db.session.execute(db.select(Item))
    items = result.scalars().all()
    return render_template("index.html", items=items)


@app.route('/add_item', methods=["GET", "POST"])
def add_item():
    add_item_form = AddNewItemForm()

    if request.method == 'POST':
        if add_item_form.validate_on_submit():
            new_item = Item(
                category=add_item_form.category.data,
                name=add_item_form.name.data,
                unit=add_item_form.unit.data,
                price=int(add_item_form.price.data * 100),
                image_url=add_item_form.image_url.data
                )

            db.session.add(new_item)
            db.session.commit()

            return redirect(url_for('home'))

    return render_template("new_item.html", form=add_item_form)


@app.route('/basket')
def show_basket():
    return render_template("basket.html")


if __name__ == "__main__":
    app.run(debug=True)
