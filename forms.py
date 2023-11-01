from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, URL


UNITS_CHOICES = [('g', 'gram'), ('kg', 'kilogram'), ('ml', 'millilitre'), ('L', 'litre'), ('p', 'piece')]
CATEGORIES_CHOICES = ['Biscuit', 'Bread', 'Brownie', 'Bun', 'Cake', 'Cheesecake', 'Cupcake', 'Donut',
                      'Loaf', 'Pastry', 'Pie', 'Pudding', 'Tart']


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign me up")


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign me up")


class AddNewItemForm(FlaskForm):
    category = SelectField("Category", choices=CATEGORIES_CHOICES, validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    unit = SelectField("Unit", choices=UNITS_CHOICES, validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    image_url = StringField("Item image URL", validators=[DataRequired(), URL()])
    add = SubmitField("Add item")
