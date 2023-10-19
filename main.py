import os
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.config['UNSPLASH_ACCESS_KEY'] = os.environ.get('UNSPLASH_ACCESS_KEY')
app.config['UNSPLASH_SECRET_KEY'] = os.environ.get('UNSPLASH_SECRET_KEY')
Bootstrap5(app)


