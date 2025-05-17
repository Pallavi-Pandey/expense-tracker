from flask import Flask, render_template, request, redirect, url_for, send_file
from models import db, Person, Expense
from export_pdf import export_to_pdf
from collections import defaultdict
import os
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL', 'sqlite:///expenses.db').replace('postgres://', 'postgresql://').replace('&supa=base-pooler.x', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

@app.before_request
def create_tables():
    if not Person.query.all():
        default_users = ["Gokul", "Pallavi", "Srimathi", "Sarnath", "Aditi", "Sriprasad"]
        for name in default_users:
            if not Person.query.filter_by(name=name).first():
                db.session.add(Person(name=name))
        db.session.commit()

@app.route("/init_db")
def init_db():
    db.drop_all()
    return "Database initialized with new schema!"

@app.route("/")
def home():
    people = Person.query.all()
    expenses = Expense.query.order_by(Expense.id.desc()).limit(10).all()  # Show last 10 expenses
    return render_template("index.html", people=people, expenses=expenses)

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

def calculate_balances():
    expenses = Expense.query.all()
    balances = defaultdict(float)
    for e in expenses:
        payer = e.payer.name
        amount = e.amount
        participants = [p.name for p in e.participants]
        split = amount / len(participants)
        for p in participants:
            if p != payer:
                balances[p] -= split
                balances[payer] += split
    return balances, expenses

def simplify(balances):
    # Convert balances to list of tuples
    creditors = [(person, balance) for person, balance in balances.items() if balance > 0]
    debtors = [(person, -balance) for person, balance in balances.items() if balance < 0]

    # Sort creditors and debtors by amount (smallest first)
    creditors.sort(key=lambda x: x[1])
    debtors.sort(key=lambda x: x[1])
    
    transactions = []
    
    # Process all debtors
    while debtors and creditors:
        debtor, d_amt = debtors[0]  # Get smallest debt
        creditor, c_amt = creditors[0]  # Get smallest credit
        
        # Calculate amount to settle
        settled = min(d_amt, c_amt)
        
        # Add transaction
        transactions.append(f"{debtor} pays {creditor} ₹{settled:.2f}")
        
        # Update remaining amounts
        d_amt -= settled
        c_amt -= settled
        
        # Remove or update creditor
        if c_amt == 0:
            creditors.pop(0)
        else:
            creditors[0] = (creditor, c_amt)
        
        # Remove or update debtor
        if d_amt == 0:
            debtors.pop(0)
        else:
            debtors[0] = (debtor, d_amt)
    
    return transactions

@app.route("/balances")
def show_balances():
    balances, expenses = calculate_balances()
    transactions = simplify(balances)
    persons=Person.query.all()
    return render_template("balances.html", balances=balances, expenses=expenses, transactions=transactions,persons=persons)

@app.route("/export_pdf")
def export_pdf():
    balances, expenses = calculate_balances()
    transactions = simplify(balances)
    filename = "trip_summary.pdf"
    if export_to_pdf(expenses, balances, transactions, filename):
        return send_file(filename, as_attachment=True)
    return "Failed to generate PDF"

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
