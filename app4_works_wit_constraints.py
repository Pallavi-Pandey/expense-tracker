from collections import defaultdict

# People
gokul = "Gokul"
pallavi = "Pallavi"
saranth = "Saranth"
aditi = "Aditi"
srimathi = "Srimathi"
sriprasad = "Sriprasad"

# Expenses
expenses = [
    {"payer": saranth, "amount": 1000, "tag": "Wedding Gift", "participants": [gokul, pallavi, saranth]},
    {"payer": pallavi, "amount": 1745, "tag": "Laser Shooter", "participants": [gokul, pallavi, saranth, aditi, srimathi]},
    {"payer": pallavi, "amount": 419, "tag": "Pista House Biriyani", "participants": [gokul, pallavi, srimathi, saranth]},
    {"payer": pallavi, "amount": 1575, "tag": "Gameistry", "participants": [gokul, pallavi, sriprasad]},
]

# Step 1: Build who owes whom directly
debts = defaultdict(lambda: defaultdict(float))

for exp in expenses:
    payer = exp["payer"]
    amount = exp["amount"]
    participants = exp["participants"]
    share = amount / len(participants)
    for person in participants:
        if person != payer:
            debts[person][payer] += round(share, 2)

# Step 2: Combine and simplify person-to-person debts
def simplify_debts(debts):
    final_settlements = []

    people = set(debts.keys()) | {p for owers in debts.values() for p in owers}
    people = list(people)

    # Net each pair
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

    # Extract final settlements
    for debtor in debts:
        for creditor in debts[debtor]:
            amount = debts[debtor][creditor]
            if amount > 0:
                final_settlements.append(f"{debtor} pays ₹{amount:.2f} to {creditor}")

    return final_settlements

# Output
print("\nSettlement instructions (accurate with constraints):")
for line in simplify_debts(debts):
    print(line)
