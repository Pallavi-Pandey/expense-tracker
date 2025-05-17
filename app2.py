from models import db, Person, Expense
from flask import Flask
from app_2_utils import create_people,create_expenses,calculate_balances,net_balance
app = Flask(__name__)
# Use SQLite URI (creates file `expenses.db`)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    create_people()
    create_expenses()
    calculate_balances("Pallavi")
    net_balance("Pallavi")

    print("Database created successfully!")




