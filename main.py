from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
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
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(2000), nullable=False)


# class Cart(db.Model):
#     __tablename__ = "carts"
#     id = db.Column(db.Integer, primary_key=True)
#


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
                        phone_number=register_form.phone_number.data,
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
                price=int(add_item_form.price.data * 100),
                image_url=add_item_form.image_url.data,
                description=add_item_form.description.data
            )

            db.session.add(new_item)
            db.session.commit()

            return redirect(url_for('home'))

    return render_template("new_item.html", form=add_item_form)


@app.route('/basket', methods=["GET", "POST"])
def show_basket():
    if session.get('cart'):
        cart = session['cart']
        cart_items = []
        total_qty = 0
        total_price = 0

        for item in cart:
            db_item = Item.query.get(item["item_id"])
            new_item = {
                "item_id": db_item.id,
                "item_name": db_item.name,
                "item_price": db_item.price,
                "item_qty": item["item_qty"],
                "item_total_price": db_item.price * item["item_qty"]
            }
            total_qty += item["item_qty"]
            total_price += new_item["item_total_price"]
            cart_items.append(new_item)

        session['total_price_cart'] = total_price
    else:
        cart_items = []

    return render_template("basket.html", cart_items=cart_items, total_qty=total_qty, total_price=total_price)


@app.route('/cart/add_item', methods=['POST'])
def add_item_to_cart():
    item_data = request.get_json()

    if session.get('cart'):
        cart = session['cart']
        item_index = next((index for (index, item) in enumerate(cart) if item["item_id"] == item_data['item_id']), None)

        if item_index is None:
            cart.append(item_data)
        else:
            cart[item_index]["item_qty"] += 1
        session['cart'] = cart
    else:
        session['cart'] = [item_data]

    total_qty = sum(item["item_qty"] for item in session['cart'])
    session['total_qty_cart'] = total_qty

    return jsonify(result=session['total_qty_cart'])


@app.route('/cart/adjust_item_qty', methods=['PUT'])
def adjust_item_qty():
    qty_data = request.get_json()

    cart = session['cart']
    item = next((item for item in cart if item["item_id"] == qty_data['item_id']), None)
    item["item_qty"] = qty_data["item_qty"]
    session['cart'] = cart

    item_price = Item.query.get(item["item_id"]).price
    item_total_price = item_price * item["item_qty"]

    total_qty = sum(item["item_qty"] for item in session['cart'])
    session['total_qty_cart'] = total_qty

    total_price = sum((Item.query.get(item["item_id"]).price * item["item_qty"]) for item in session['cart'])
    session['total_price_cart'] = total_price

    return jsonify(result_item=item,
                   result_item_total_price=item_total_price,
                   result_total_qty=session['total_qty_cart'],
                   result_total_price=session['total_price_cart'])


@app.route('/cart/remove_item', methods=['DELETE'])
def remove_item():
    item_id = request.get_json()

    cart = session['cart']
    item = next((item for item in cart if item["item_id"] == item_id), None)
    cart.remove(item)
    session['cart'] = cart

    total_qty = sum(item["item_qty"] for item in session['cart'])
    session['total_qty_cart'] = total_qty

    total_price = sum((Item.query.get(item["item_id"]).price * item["item_qty"]) for item in session['cart'])
    session['total_price_cart'] = total_price

    return jsonify(result_total_qty=session['total_qty_cart'],
                   result_total_price=session['total_price_cart'])


if __name__ == "__main__":
    app.run(debug=True)
