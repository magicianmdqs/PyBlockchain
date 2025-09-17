class Ledger:
    def __init__(self):
        self.ledger = {}

    def add_to_ledger(self, account):
        self.ledger[account.address] = account

    def get_balance(self, address):
        try:
            balance = self.ledger[address].balance
        except KeyError:
            balance = 0
        return balance

    def update_ledger(self, tx):
        amount = tx.amount
        tax = tx.TAX
        fee = tx.FEE
        self.ledger[tx.sender_address].balance -= (amount + tax + fee)
        self.ledger[tx.sender_address].transactions.append(tx)
        self.ledger[tx.recv].transactions.append(tx)
        self.ledger["SYSTEM"].balance += (tax + fee)
        try:
            self.ledger[tx.recv].balance += amount
        except KeyError:
            self.ledger[tx.recv].balance = amount

    def to_json(self):
        return self.ledger
