from flask import Flask, render_template, request, redirect, url_for, send_file
from models import db, Person, Expense
from export_pdf import export_to_pdf
from collections import defaultdict
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL', 'sqlite:///expenses.db').replace('postgres://', 'postgresql://').replace('&supa=base-pooler.x', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()
    # Initialize with default users if none exist
    if not Person.query.all():
        default_users = ["Gokul", "Pallavi", "Srimathi", "Sarnath", "Aditi", "Sriprasad"]
        for name in default_users:
            if not Person.query.filter_by(name=name).first():
                db.session.add(Person(name=name))
        db.session.commit()

@app.route("/")
def home():
    people = Person.query.all()
    return render_template("index.html", people=people)

@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    people = Person.query.all()
    if request.method == "POST":
        payer = request.form["payer"]
        amount = float(request.form["amount"])
        participants = request.form.getlist("participants")
        tag = request.form["tag"]

        exp = Expense(payer=payer, amount=amount, tag=tag, participants=",".join(participants))
        db.session.add(exp)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_expense.html", people=people)

def calculate_balances():
    expenses = Expense.query.all()
    balances = defaultdict(float)
    for e in expenses:
        payer = e.payer
        amount = e.amount
        participants = e.participants.split(",")
        split = amount / len(participants)
        for p in participants:
            if p != payer:
                balances[p] -= split
                balances[payer] += split
    return balances, expenses

def simplify(balances):
    creditors = []
    debtors = []

    for person, balance in balances.items():
        if balance > 0:
            creditors.append((person, balance))
        elif balance < 0:
            debtors.append((person, -balance))

    creditors.sort(key=lambda x: x[1])
    debtors.sort(key=lambda x: x[1])
    transactions = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, d_amt = debtors[i]
        creditor, c_amt = creditors[j]
        settled = min(d_amt, c_amt)
        transactions.append(f"{debtor} pays {creditor} ₹{settled:.2f}")
        debtors[i] = (debtor, d_amt - settled)
        creditors[j] = (creditor, c_amt - settled)
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return transactions

@app.route("/balances")
def show_balances():
    balances, expenses = calculate_balances()
    transactions = simplify(balances)
    return render_template("balances.html", balances=balances, expenses=expenses, transactions=transactions)

@app.route("/export_pdf")
def export_pdf():
    balances, expenses = calculate_balances()
    transactions = simplify(balances)
    filename = "trip_summary.pdf"
    if export_to_pdf(expenses, balances, transactions, filename):
        return send_file(filename, as_attachment=True)
    return "Failed to generate PDF"

if __name__ == "__main__":
    app.run(debug=True)
