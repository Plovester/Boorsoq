from flask import render_template, redirect, url_for, request, flash, session, jsonify, abort, json
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, literal, select
from datetime import datetime, date
from dateutil import parser
from functools import wraps
from app import login_manager, create_app
from database import db
from models import User, Role, Category, Item, OrderItem, Order, UserRoles
from forms import SearchForm, RegisterForm, LoginForm, AddNewItemForm, AddNewCategoryForm
from create_token import generate_token, confirm_token

app = create_app()
mail = Mail(app)


def admin_only(function):
    @wraps(function)
    def check_credentials(*args, **kwargs):
        is_admin = False

        for role in current_user.roles:
            if role.name == "Admin":
                is_admin = True

        if is_admin:
            return function(*args, **kwargs)
        else:
            return abort(403)

    return check_credentials


def check_if_confirmed(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash("Please confirm your account!", "warning")
            return redirect(url_for("inactive"))
        return function(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def home(page=1):
    search_form = SearchForm()
    items = Item.query.paginate(page=page, per_page=10, error_out=False)
    pages_numbers = items.iter_pages(left_edge=2, left_current=2, right_edge=2, right_current=2)

    if request.method == 'POST':
        searching_item = search_form.item.data
        return redirect(url_for('show_searching_items', searching_item=searching_item))

    return render_template("index.html",
                           items=items,
                           pages=pages_numbers,
                           current_page=page,
                           search_form=search_form)


@app.route('/categories')
def get_categories():
    categories = db.session.execute(select(Category)).scalars().all()

    return render_template("categories.html", categories=categories)


@app.route('/categories/<int:id>')
def show_category(id):
    page = request.args.get('page')

    if page:
        try:
            page = int(page)
        except:
            return render_template("errors/error.html")
    else:
        page = 1

    category = Category.query.filter_by(id=id).first()

    items = Item.query.filter_by(category_id=id).paginate(page=page, per_page=10, error_out=False)
    pages_numbers = items.iter_pages(left_edge=2, left_current=2, right_edge=2, right_current=2)

    return render_template("items_by_category.html",
                           category=category,
                           items=items,
                           pages=pages_numbers,
                           current_page=page)


@app.route('/contact')
def contacts_page():
    return render_template("contacts.html")


@app.route('/search')
def show_searching_items():
    searching_item = request.args['searching_item']
    result = Item.query.filter(Item.name.ilike('%%' + literal(searching_item) + '%%')).all()
    return render_template('searched_items.html', items=result)


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()

    if not current_user.is_authenticated:
        if request.method == 'POST':
            user = User.query.filter_by(email=register_form.email.data).first()

            if not user:
                if register_form.validate_on_submit():
                    user_role = Role.query.filter_by(name='User').first()
                    hashed_password = generate_password_hash(register_form.password.data, method='pbkdf2:sha256', salt_length=8)

                    new_user = User(
                        name=register_form.name.data,
                        phone_number=register_form.phone_number.data,
                        email=register_form.email.data,
                        password=hashed_password,
                        registered_on=datetime.now()
                    )

                    new_user.roles.append(user_role)

                    db.session.add(new_user)
                    db.session.commit()

                    token = generate_token(app, register_form.email.data)
                    confirm_url = url_for('confirm_email', token=token, _external=True)
                    html = render_template("confirm_email.html", confirm_url=confirm_url)
                    subject = "Please confirm your email"

                    msg = Message(
                        subject,
                        recipients=[new_user.email],
                        html=html,
                        sender="noreply@boorsoq.com"
                    )

                    mail.send(msg)

                    login_user(new_user)

                    flash("A confirmation email has been sent via email", "success")

                    return redirect(url_for('inactive'))
            else:
                flash('The email has already exist. Try to log in')
                return redirect(url_for('login'))

        return render_template("register.html", register_form=register_form)


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    if current_user.confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for('home'))

    email = confirm_token(app, token)
    user = User.query.filter_by(email=current_user.email).first()

    if user.email == email:
        user.confirmed = True
        user.confirmed_on = datetime.now()

        db.session.add(user)
        db.session.commit()

        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    return redirect(url_for('home'))


@app.route('/inactive')
@login_required
def inactive():
    if current_user.confirmed:
        return redirect(url_for('home'))
    return render_template('inactive.html')


@app.route('/resend')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash("Your account has already been confirmed", "success")
        return redirect(url_for('home'))
    token = generate_token(app, current_user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template("confirm_email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"

    msg = Message(
        subject,
        recipients=[current_user.email],
        html=html,
        sender="noreply@boorsoq.com"
    )

    mail.send(msg)

    flash("A new confirmation email has been sent", "success")
    return redirect(url_for('inactive'))


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

                        for role in current_user.roles:
                            if role.name == "Admin":
                                return redirect(url_for('admin_panel'))
                            elif role.name == "User":
                                return redirect(url_for('home'))
                    else:
                        flash('Your password is not correct. Try again')
                        return redirect(url_for('login'))
                else:
                    flash('The email does not exist. Try again or register')
                    return redirect(url_for('login'))

    return render_template("login.html", login_form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user_profile')
@login_required
@check_if_confirmed
def show_user_account():
    return render_template("user_profile.html")


@app.route('/user_settings')
@login_required
@check_if_confirmed
def user_settings():
    return render_template("user_settings.html")


@app.route('/user_info', methods=['PUT'])
@login_required
@check_if_confirmed
def edit_user_info():
    parameter = request.get_json()
    db.session.query(User).filter(User.id == current_user.id).update(parameter, synchronize_session=False)
    db.session.commit()

    user = User.query.filter_by(id=current_user.id).first()
    user_info = {
        'name': user.name,
        'email': user.email,
        'phone_number': user.phone_number
    }
    return jsonify(user_info)


@app.route('/user_settings/password', methods=['PUT'])
@login_required
@check_if_confirmed
def edit_user_password():
    user_password_info = request.get_json()
    user = User.query.filter_by(id=current_user.id).first()

    is_password_correct = check_password_hash(user.password, user_password_info['old_password'])

    if is_password_correct:
        new_password = generate_password_hash(user_password_info['new_password'], method='pbkdf2:sha256', salt_length=8)
        db.session.query(User).filter(User.id == current_user.id).update({'password': new_password}, synchronize_session=False)
        db.session.commit()
    else:
        print('Error')

    return "Success", 204


@app.route('/orders_history')
@login_required
@check_if_confirmed
def orders_history():
    page = request.args.get('page')

    if page:
        try:
            page = int(page)
        except:
            return render_template("errors/error.html")
    else:
        page = 1

    user_orders = (db.session.query(Order)
                   .filter(Order.user_id == current_user.id)
                   .order_by(Order.id.desc())
                   .paginate(page=page, per_page=20, error_out=False))

    pages_numbers = user_orders.iter_pages(left_edge=2, left_current=2, right_edge=2, right_current=2)

    return render_template("user_orders_history.html",
                           pages=pages_numbers,
                           orders=user_orders,
                           current_page=page)


@app.route('/basket', methods=["GET", "POST"])
@login_required
@check_if_confirmed
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
@check_if_confirmed
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
@check_if_confirmed
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
@check_if_confirmed
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
@check_if_confirmed
def checkout():
    cart = session['cart']
    total_price = session['total_price_cart']
    total_qty = session['total_qty_cart']

    cart_items = []
    deleted_items = []

    for item in cart:
        db_item = Item.query.get(item["item_id"])

        current_item = {
            "item_id": db_item.id,
            "item_name": db_item.name,
            "item_price": db_item.price,
            "item_qty": item["item_qty"],
            "item_total_price": db_item.price * item["item_qty"],
            "item_image_url": db_item.image_url,
        }

        if db_item.deleted_at:
            deleted_items.append(current_item)
        else:
            cart_items.append(current_item)

    if len(deleted_items) > 0:
        for product in deleted_items:
            for item in cart:
                if product['item_id'] == item['item_id']:
                    cart.remove(item)
                    session['cart'] = cart

            total_qty -= product["item_qty"]
            session['total_qty_cart'] = total_qty

            total_price -= product["item_total_price"]
            session['total_price_cart'] = total_price

        return render_template("unavailable_items.html", items=deleted_items)

    return render_template("checkout.html", cart_items=cart_items, total_qty=total_qty, total_price=total_price)


@app.route('/confirm_order', methods=["POST"])
@login_required
@check_if_confirmed
def confirm_order():
    ready_by_date = request.get_json()

    if not ready_by_date:
        ready_by_date = date.today()
    else:
        ready_by_date = datetime.strptime(ready_by_date, '%d/%m/%Y').date()

    cart = session['cart']

    new_order = Order(
        user_id=current_user.id,
        created_at=date.today(),
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
            created_at=ready_by_date,
            item_id=db_item.id,
            order_id=new_order.id
        )

        db.session.add(new_order_item)
        db.session.commit()

    session['cart'] = []
    session['total_price_cart'] = 0
    session['total_qty_cart'] = 0

    return "Success", 204


@app.route('/admin/orders')
@login_required
@admin_only
def admin_panel():
    page = request.args.get('page')

    if page:
        try:
            page = int(page)
        except:
            return render_template("errors/error.html")
    else:
        page = 1

    orders = Order.query.paginate(page=page, per_page=20, error_out=False)

    pages_numbers = orders.iter_pages(left_edge=2, left_current=2, right_edge=2, right_current=2)

    return render_template("admin_panel/admin_panel.html",
                           orders=orders,
                           pages=pages_numbers,
                           current_page=page)


@app.route('/admin/orders/<int:order_id>', methods=['PUT'])
@login_required
@admin_only
def change_order_details(order_id):
    changes = request.get_json()

    db.session.query(Order).filter(Order.id == order_id).update(changes, synchronize_session=False)
    db.session.commit()

    order = Order.query.filter_by(id=order_id).first()
    order_data = {
        'status': order.status
    }

    return jsonify(order_data)


@app.route('/admin/products')
@login_required
@admin_only
def admin_panel_products():
    page = request.args.get('page')

    if page:
        try:
            page = int(page)
        except:
            return render_template("errors/error.html")
    else:
        page = 1

    products = Item.query.paginate(page=page, per_page=20, error_out=False)
    pages_numbers = products.iter_pages(left_edge=2, left_current=2, right_edge=2, right_current=2)
    categories = Category.query.filter_by(deleted_at=None)

    return render_template("admin_panel/admin_panel_products.html",
                           products=products,
                           categories=categories,
                           pages=pages_numbers,
                           current_page=page
                           )


@app.route('/admin/products/add_item', methods=["GET", "POST"])
@login_required
@admin_only
def add_item():
    categories = Category.query.filter_by(deleted_at=None)
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


@app.route('/admin/products/<int:product_id>', methods=['PUT'])
@login_required
@admin_only
def edit_product_params(product_id):
    new_product_data = request.get_json()

    db.session.query(Item).filter(Item.id == product_id).update(new_product_data, synchronize_session=False)
    db.session.commit()

    product = Item.query.filter_by(id=product_id).first()
    product_data = {
        'name': product.name,
        'category': product.category.name,
        'price': product.price,
        'image_url': product.image_url,
        'description': product.description,
        'visibility': product.visibility
    }

    return jsonify(product_data)


@app.route('/admin/products/deletion_product/<int:product_id>', methods=['POST'])
@login_required
@admin_only
def delete_product(product_id):
    if request.method == 'POST':
        deleted_at = date.today()
        db.session.query(Item).filter(Item.id == product_id).update({'deleted_at': deleted_at,
                                                                     'visibility': 0,
                                                                     'category_id': None},
                                                                    synchronize_session=False)
        db.session.commit()

        return redirect(url_for('admin_panel_products'))


@app.route('/admin/categories')
@login_required
@admin_only
def admin_panel_categories():
    categories = Category.query.filter_by(deleted_at=None)

    return render_template("admin_panel/admin_panel_categories.html",
                           categories=categories)


@app.route('/admin/categories/add_category', methods=["GET", "POST"])
@login_required
@admin_only
def add_category():
    add_category_form = AddNewCategoryForm()

    if request.method == "POST":
        if add_category_form.validate_on_submit():
            new_category = Category(
                name=add_category_form.name.data,
                image_url=add_category_form.image_url.data
            )

            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('admin_panel_categories'))

    return render_template("admin_panel/new_item_or_category.html", form=add_category_form)


@app.route('/admin/categories/<int:category_id>', methods=['PUT'])
@login_required
@admin_only
def edit_category_params(category_id):
    new_category_data = request.get_json()

    db.session.query(Category).filter(Category.id == category_id).update(new_category_data, synchronize_session=False)
    db.session.commit()

    category_name = Category.query.filter_by(id=category_id).first().name
    image_url = Category.query.filter_by(id=category_id).first().image_url

    return jsonify({'name': category_name, 'image_url': image_url})


@app.route('/admin/categories/deletion_category/<int:category_id>', methods=['POST'])
@login_required
@admin_only
def delete_category(category_id):
    if request.method == 'POST':
        deleted_at = date.today()

        category = Category.query.filter_by(id=category_id).first()

        if len(category.items) > 0:
            return render_template("admin_panel/admin_panel_category_for_deletion.html", category=category)
        else:
            db.session.query(Category).filter(Category.id == category_id).update({'deleted_at': deleted_at},
                                                                                 synchronize_session=False)
            db.session.commit()

        return redirect(url_for('admin_panel_categories'))


@app.route('/admin/customers')
@login_required
@admin_only
def admin_panel_customers():
    page = request.args.get('page')

    if page:
        try:
            page = int(page)
        except:
            return render_template("errors/error.html")
    else:
        page = 1

    customers = (db.session.query(User)
                 .join(UserRoles)
                 .join(Role)
                 .filter(Role.name == "User")
                 .paginate(page=page, per_page=10, error_out=False))

    pages_numbers = customers.iter_pages(left_edge=2, left_current=2, right_edge=2, right_current=2)

    return render_template("admin_panel/admin_panel_customers.html",
                           customers=customers,
                           pages=pages_numbers,
                           current_page=page)


@app.route('/admin/reports')
@login_required
@admin_only
def admin_panel_reports():
    return render_template("admin_panel/admin_panel_reports.html")


@app.route('/admin/reports/number_of_orders', methods=["GET", "POST"])
@login_required
@admin_only
def number_of_orders():
    dates_range = request.get_json()

    orders = (db.session.query(Order.status, func.count(Order.status)).group_by(Order.status)
              .filter(Order.created_at <= parser.parse(dates_range['date_end']))
              .filter(Order.created_at >= parser.parse(dates_range['date_start'])).all())

    orders_by_statuses = {
        'New': 0,
        'Confirmed': 0,
        'In progress': 0,
        'Ready': 0,
        'Canceled': 0,
        'Completed': 0
    }

    for row in orders:
        for status in orders_by_statuses:
            if row[0].capitalize() == status:
                orders_by_statuses[status] = row[1]

    return json.dumps(orders_by_statuses, sort_keys=False)


@app.route('/admin/reports/most_popular_products', methods=["GET", "POST"])
@login_required
@admin_only
def most_popular_products():
    dates_range = request.get_json()

    products = sorted(((db.session.query(OrderItem.item_id, func.sum(OrderItem.quantity).label('quantity'))
                        .group_by(OrderItem.item_id))
                        .filter(OrderItem.created_at <= parser.parse(dates_range['date_end']))
                        .filter(OrderItem.created_at >= parser.parse(dates_range['date_start'])).all()),
                      key=lambda tup: tup[1], reverse=True)[:5]

    popular_products = {}

    for product in products:
        product_name = Item.query.filter_by(id=product[0]).first()

        popular_products[product_name.name] = product[1]

    return json.dumps(popular_products, sort_keys=False)


@app.route('/admin/settings')
@login_required
@admin_only
def admin_panel_settings():
    return render_template("admin_panel/admin_panel_settings.html")


@app.route('/admin/new_admin', methods=["GET", "POST"])
@login_required
@admin_only
def create_new_admin():
    new_admin_data = request.get_json()

    admin = User.query.filter_by(email=new_admin_data['email']).first()

    if not admin:
        role = Role.query.filter_by(name='Admin').first()

        hashed_password = generate_password_hash(new_admin_data['password'], method='pbkdf2:sha256',
                                                 salt_length=8)

        new_admin = User(
            name=new_admin_data['name'],
            phone_number=new_admin_data['phone_number'],
            email=new_admin_data['email'],
            password=hashed_password
        )

        new_admin.roles.append(role)

        db.session.add(new_admin)
        db.session.commit()

    return render_template("admin_panel/admin_panel_settings.html")


if __name__ == "__main__":
    app.run(debug=True)

