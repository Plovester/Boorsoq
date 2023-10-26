from flask import Flask, render_template, redirect, url_for, request
# from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
Bootstrap5(app)

# login_manager = LoginManager()
# login_manager.init_app(app)


@app.route('/')
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
