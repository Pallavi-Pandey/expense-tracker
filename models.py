from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

expense_participants = db.Table(
    'expense_participants',
    db.Column('expense_id', db.Integer, db.ForeignKey('expenses.id'), primary_key=True),
    db.Column('person_id', db.Integer, db.ForeignKey('people.id'), primary_key=True)
)

class Person(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationship for expenses where this person is the payer
    paid_expenses = db.relationship('Expense', foreign_keys='Expense.payer_id')
    # Relationship for expenses where this person is a participant
    shared_expenses = db.relationship('Expense', secondary=expense_participants)

    def __repr__(self):
        return f"Person('{self.name}')"

    def __str__(self):
        return self.name

   

    @property
    def to_pay(self):
        total = 0
        for expense in self.shared_expenses:
            if expense.payer != self:  # Only count expenses where we're not the payer
                total += expense.amount / len(expense.participants)
        return total
    
    @property
    def to_pay_details(self):
        details = []
        for expense in self.shared_expenses:
            if expense.payer != self:
                details.append({
                    'expense': expense,
                    'amount': expense.amount / len(expense.participants)
                })
        return details

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    payer_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tag = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    payer = db.relationship('Person', foreign_keys=[payer_id])
    participants = db.relationship('Person', secondary=expense_participants)

    def __repr__(self):
        return f"Expense('{self.payer.name}', {self.amount}, {self.tag})"

    def save(self):
        db.session.add(self)
        db.session.commit()
    
 