from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bootstrap import Bootstrap5
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, AddNewItemForm, AddNewCategoryForm
from datetime import date
import os

app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
db = SQLAlchemy()
migrate = Migrate(app,  db, command='migrate')
db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    orders = relationship("Order", back_populates="user")


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    items = relationship("Item", back_populates="category")


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    category = relationship("Category", back_populates="items")
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    visibility = db.Column(db.Boolean, nullable=False)
    order_items = relationship("OrderItem", uselist=False, back_populates="item")


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    item = relationship("Item", back_populates="order_items")
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    order = relationship("Order", back_populates="order_items")
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user = relationship("User", back_populates="orders")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.String(250), nullable=False)
    ready_by_date = db.Column(db.String(250), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(250), nullable=False)
    order_items = relationship("OrderItem", back_populates="order")


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    items = db.session.execute(db.select(Item)).scalars().all()

    return render_template("index.html", items=items)


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
                    return redirect(url_for('login'))

    return render_template("register.html", form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user_profile')
@login_required
def show_user_account():
    return render_template("user_profile.html")


@app.route('/user_settings')
@login_required
def user_settings():
    return render_template("user_settings.html")


@app.route('/user_settings/<int:user_id>', methods=['PUT'])
@login_required
def edit_user_info(user_id):
    parameter = request.get_json()
    db.session.query(User).filter(User.id == user_id).update(parameter, synchronize_session=False)
    db.session.commit()
    user = User.query.filter_by(id=user_id).first()
    user_info = {
        'name': user.name,
        'email': user.email,
        'phone_number': user.phone_number
    }
    return jsonify(user_info)


@app.route('/user_settings/<int:user_id>/password', methods=['PUT'])
@login_required
def edit_user_password(user_id):
    user_password_info = request.get_json()
    user = User.query.filter_by(id=user_id).first()

    is_password_correct = check_password_hash(user.password, user_password_info['old_password'])

    if is_password_correct:
        new_password = generate_password_hash(user_password_info['new_password'], method='pbkdf2:sha256', salt_length=8)
        db.session.query(User).filter(User.id == user_id).update({'password': new_password}, synchronize_session=False)
        db.session.commit()
    else:
        print('Error')

    return "Success", 204


@app.route('/orders_history/<int:user_id>')
@login_required
def orders_history(user_id):
    user_orders = db.session.execute(db.select(Order).where(Order.user_id == user_id)).scalars().all()

    reversed_orders_list = reversed(user_orders)

    return render_template("user_orders_history.html", orders=reversed_orders_list)


@app.route('/add_category', methods=["GET", "POST"])
@login_required
def add_category():
    add_category_form = AddNewCategoryForm()

    if request.method == "POST":
        if add_category_form.validate_on_submit():
            new_category = Category(
                name=add_category_form.name.data,
            )

            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('admin_panel_products'))

    return render_template("admin_panel/new_item_or_category.html", form=add_category_form)


@app.route('/add_item', methods=["GET", "POST"])
@login_required
def add_item():
    categories = db.session.execute(db.select(Category)).scalars().all()
    add_item_form = AddNewItemForm()
    add_item_form.category.choices = sorted([category.name for category in categories])

    if request.method == "POST":
        if add_item_form.validate_on_submit():
            category = Category.query.filter_by(name=add_item_form.category.data).first()
            new_item = Item(
                category_id=category.id,
                name=add_item_form.name.data,
                price=int(add_item_form.price.data * 100),
                image_url=add_item_form.image_url.data,
                description=add_item_form.description.data,
                visibility=add_item_form.visibility.data
            )

            db.session.add(new_item)
            db.session.commit()

            return redirect(url_for('admin_panel_products'))

    return render_template("admin_panel/new_item_or_category.html", form=add_item_form)


@app.route('/basket', methods=["GET", "POST"])
@login_required
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
        total_qty = 0
        total_price = 0

    return render_template("basket.html", cart_items=cart_items, total_qty=total_qty, total_price=total_price)


@app.route('/cart/add_item', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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


@app.route('/checkout', methods=["GET", "POST"])
@login_required
def checkout():
    cart = session['cart']
    total_price = session['total_price_cart']
    total_qty = session['total_qty_cart']

    cart_items = []
    for item in cart:
        db_item = Item.query.get(item["item_id"])
        new_item = {
            "item_id": db_item.id,
            "item_name": db_item.name,
            "item_price": db_item.price,
            "item_qty": item["item_qty"],
            "item_total_price": db_item.price * item["item_qty"],
            "item_image_url": db_item.image_url
        }
        cart_items.append(new_item)

    return render_template("checkout.html", cart_items=cart_items, total_qty=total_qty, total_price=total_price)


@app.route('/confirm_order', methods=["POST"])
@login_required
def confirm_order():
    ready_by_date = request.get_json()
    cart = session['cart']

    new_order = Order(
        user_id=current_user.id,
        created_at=date.today().strftime("%d/%m/%Y"),
        ready_by_date=ready_by_date,
        total_price=session['total_price_cart'],
        status='new'
    )

    db.session.add(new_order)
    db.session.commit()

    for item in cart:
        db_item = Item.query.get(item["item_id"])

        new_order_item = OrderItem(
            price=db_item.price,
            quantity=item["item_qty"],
            item_id=db_item.id,
            order_id=new_order.id
        )

        db.session.add(new_order_item)
        db.session.commit()

    session['cart'] = []
    session['total_price_cart'] = 0
    session['total_qty_cart'] = 0

    return "Success", 204


@app.route('/orders')
@login_required
def admin_panel():
    orders = db.session.execute(db.select(Order)).scalars().all()

    return render_template("admin_panel/admin_panel.html", orders=orders)


@app.route('/products')
@login_required
def admin_panel_products():
    products = db.session.execute(db.select(Item)).scalars().all()
    categories = db.session.execute(db.select(Category)).scalars().all()

    return render_template("admin_panel/admin_panel_products.html", products=products, categories=categories)


@app.route('/customers')
@login_required
def admin_panel_customers():
    users = db.session.execute(db.select(User)).scalars().all()
    customers = []
    for user in users:
        customer = {
            'id': user.id,
            'name': user.name,
            'phone_number': user.phone_number,
            'email': user.email
        }
        customers.append(customer)

    return render_template("admin_panel/admin_panel_customers.html", customers=customers)


@app.route('/reports')
@login_required
def admin_panel_reports():
    return render_template("admin_panel/admin_panel_reports.html")


@app.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def change_order_status(order_id):
    new_status = request.get_json()

    db.session.query(Order).filter(Order.id == order_id).update(new_status, synchronize_session=False)
    db.session.commit()

    return "Success", 204


@app.route('/products/<int:product_id>', methods=['PUT'])
@login_required
def edit_product_params(product_id):
    new_product_data = request.get_json()

    db.session.query(Item).filter(Item.id == product_id).update(new_product_data, synchronize_session=False)
    db.session.commit()

    product = Item.query.filter_by(id=product_id).first()
    product_data = {
        'name': product.name,
        'price': product.price,
        'image_url': product.image_url,
        'description': product.description,
        'visibility': product.visibility
    }

    return jsonify(product_data)


if __name__ == "__main__":
    app.run(debug=True)

