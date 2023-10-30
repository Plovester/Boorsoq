from flask import Flask, render_template, redirect, url_for, request
# from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap5
from forms import RegisterForm, LoginForm
import os

app = Flask(__name__)
Bootstrap5(app)

# login_manager = LoginManager()
# login_manager.init_app(app)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    return render_template("register.html", form=register_form)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    return render_template("register.html", form=login_form)


if __name__ == "__main__":
    app.run(debug=True)
