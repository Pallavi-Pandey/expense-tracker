from collections import defaultdict
import itertools

# List of names for reference
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

# Step 1: Compute net balances
balances = defaultdict(float)

for exp in expenses:
    payer = exp["payer"]
    amount = exp["amount"]
    participants = exp["participants"]
    share = amount / len(participants)
    for person in participants:
        balances[person] -= share
    balances[payer] += amount

# Filter zero balances and prepare list
net_balances = list(filter(lambda x: round(x[1], 2) != 0, balances.items()))

# Step 2: Minimize transactions using DFS
def dfs(start, amounts):
    while start < len(amounts) and round(amounts[start], 2) == 0:
        start += 1
    if start == len(amounts):
        return 0
    min_txns = float('inf')
    for i in range(start + 1, len(amounts)):
        if amounts[start] * amounts[i] < 0:
            amounts[i] += amounts[start]
            min_txns = min(min_txns, 1 + dfs(start + 1, amounts))
            amounts[i] -= amounts[start]
    return min_txns

# Just minimum number of transactions
print("Minimum transactions needed:", dfs(0, [amt for _, amt in net_balances]))

# Step 3 (optional): Get actual settlement instructions
def settle_debts(balances_dict):
    from heapq import heappush, heappop

    creditors = []
    debtors = []
    for person, amt in balances_dict.items():
        amt = round(amt, 2)
        if amt > 0:
            heappush(creditors, (-amt, person))  # max heap
        elif amt < 0:
            heappush(debtors, (amt, person))     # min heap

    settlements = []
    while creditors and debtors:
        credit_amt, creditor = heappop(creditors)
        debit_amt, debtor = heappop(debtors)

        settled_amt = min(-debit_amt, -credit_amt)
        settlements.append(f"{debtor} pays ₹{settled_amt:.2f} to {creditor}")

        new_credit = credit_amt + settled_amt
        new_debit = debit_amt + settled_amt

        if round(new_credit, 2) != 0:
            heappush(creditors, (new_credit, creditor))
        if round(new_debit, 2) != 0:
            heappush(debtors, (new_debit, debtor))
    
    return settlements

print("\nSettlement instructions:")
for s in settle_debts(balances):
    print(s)
