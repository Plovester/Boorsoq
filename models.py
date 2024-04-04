from flask_login import UserMixin
from sqlalchemy.orm import relationship
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    orders = relationship("Order", back_populates="user")


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    items = relationship("Item", back_populates="category")
    deleted_at = db.Column(db.DateTime)


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    category = relationship("Category", back_populates="items")
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    visibility = db.Column(db.Boolean, nullable=False)
    deleted_at = db.Column(db.DateTime)
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
