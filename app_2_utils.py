from models import db, Person,Expense

def create_people():
    default_users = ["Gokul", "Pallavi", "Srimathi", "Sarnath", "Aditi", "Sriprasad"]
    for name in default_users:
        if not Person.query.filter_by(name=name).first():
            db.session.add(Person(name=name))
    db.session.commit()
    

def create_expenses():
    # saranath paid 1000 (gokul,pallavi,saranath)
    
    saranth=Person.query.filter_by(name="Sarnath").first()
    gokul=Person.query.filter_by(name="Gokul").first()
    pallavi=Person.query.filter_by(name="Pallavi").first()
    aditi=Person.query.filter_by(name="Aditi").first()
    srimathi=Person.query.filter_by(name="Srimathi").first()
    sriprasad=Person.query.filter_by(name="Sriprasad").first()
    
    wedding_gift=Expense(payer=saranth,amount=1000,tag="Wedding Gift",participants=[gokul,pallavi,saranth]).save()
    laser_shooter=Expense(payer=pallavi,amount=1745,tag="Laser Shooter",participants=[gokul,pallavi,saranth,aditi,srimathi]).save()
    # Pallavi paid ₹419.0 Gokul, Pallavi, Srimathi, Sarnath [Tag: pista house biriyani]
    pistah_house=Expense(payer=pallavi,amount=419,tag="Pista House Biriyani",participants=[gokul,pallavi,srimathi,saranth]).save()
    # Pallavi paid ₹1575.0 Gokul, Pallavi, Sriprasad [Tag: gameistry]
    gameistry=Expense(payer=pallavi,amount=1575,tag="Gameistry",participants=[gokul,pallavi,sriprasad]).save()
    

def calculate_balances(person):
    person=Person.query.filter_by(name=person).first()
    print(person)
    expense_participation=person.shared_expenses
    print(expense_participation)

def net_balance(person):
    person=Person.query.filter_by(name=person).first()
    print(person)
    all_expenses=Expense.query.all()
    person_dict={}
    people=Person.query.all()
    for person in people:
        person_dict[person.name]=0
    for expense in all_expenses:
        if expense.payer==person:
           
    print(person_dict)
    