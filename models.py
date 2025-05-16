from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer = db.Column(db.String)
    amount = db.Column(db.Float)
    tag = db.Column(db.String)
    participants = db.Column(db.String)  # Comma-separated names
