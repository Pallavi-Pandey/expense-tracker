# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import  SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, Person, Expense
from collections import defaultdict
import os

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL', 'sqlite:///expenses.db').replace('postgres://', 'postgresql://').replace('&supa=base-pooler.x', '')

db.init_app(app)

from dotenv import load_dotenv
load_dotenv()


def create_tables():
    db.create_all()

@app.route('/')
def index():
    people = Person.query.all()
    expenses = Expense.query.all()
    return render_template('index2.html', people=people, expenses=expenses)

@app.route('/settlements')
def settlements():
    debts = defaultdict(lambda: defaultdict(float))

    for expense in Expense.query.all():
        payer = expense.payer
        participants = expense.participants
        amount = expense.amount
        share = amount / len(participants)

        for person in participants:
            if person != payer:
                debts[person.name][payer.name] += round(share, 2)

    settlements = simplify_debts(debts)
    return render_template('settlements.html', settlements=settlements)

def simplify_debts(debts):
    final_settlements = []
    people = set(debts.keys()) | {p for owers in debts.values() for p in owers}
    people = list(people)

    for p1 in people:
        for p2 in people:
            if p1 != p2:
                amt1 = debts[p1].get(p2, 0)
                amt2 = debts[p2].get(p1, 0)
                if amt1 > amt2:
                    debts[p1][p2] = round(amt1 - amt2, 2)
                    debts[p2][p1] = 0
                elif amt2 > amt1:
                    debts[p2][p1] = round(amt2 - amt1, 2)
                    debts[p1][p2] = 0
                else:
                    debts[p1][p2] = 0
                    debts[p2][p1] = 0

    for debtor in debts:
        for creditor in debts[debtor]:
            amount = debts[debtor][creditor]
            if amount > 0:
                final_settlements.append(f"{debtor} pays ₹{amount:.2f} to {creditor}")
    return final_settlements

@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    people = Person.query.all()
    if request.method == "POST":
        payer = request.form["payer"]
        amount = float(request.form["amount"])
        participants = request.form.getlist("participants")
        tag = request.form["tag"]

        # First get all participant objects
        participant_objects = []
        for participant_name in participants:
            participant = Person.query.filter_by(name=participant_name).first()
            if participant:
                participant_objects.append(participant)
        
        # Create expense with payer
        payer_person = Person.query.filter_by(name=payer).first()
        if not payer_person:
            return "Error: Payer not found", 400
        
        exp = Expense(payer=payer_person, amount=amount, tag=tag)
        
        # Add participants after expense is created
        for participant in participant_objects:
            exp.participants.append(participant)
        db.session.add(exp)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_expense.html", people=people)

@app.route("/edit_expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    people = Person.query.all()
    
    if request.method == "POST":
        expense.payer = Person.query.filter_by(name=request.form["payer"]).first()
        expense.amount = float(request.form["amount"])
        expense.tag = request.form["tag"]
        
        # Clear existing participants
        expense.participants.clear()
        
        # Add new participants
        for participant_name in request.form.getlist("participants"):
            participant = Person.query.filter_by(name=participant_name).first()
            if participant:
                expense.participants.append(participant)
        
        db.session.commit()
        return redirect(url_for("home"))
    
    selected_participants = [p.name for p in expense.participants]
    return render_template("edit_expense.html", expense=expense, people=people, selected_participants=selected_participants, participants=selected_participants)

@app.route("/delete_expense/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
