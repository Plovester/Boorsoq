from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, BooleanField
from wtforms.validators import DataRequired, URL


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired()])
    phone_number = StringField("Phone number", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign me up")


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign me up")


class AddNewItemForm(FlaskForm):
    category = SelectField("Category", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    image_url = StringField("Item image URL", validators=[DataRequired(), URL()])
    description = StringField("Description", validators=[DataRequired()])
    visibility = BooleanField("Visible", default=True)
    add = SubmitField("Add item")


class AddNewCategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    image_url = StringField("Category image URL", validators=[DataRequired(), URL()])
    add = SubmitField("Add category")
