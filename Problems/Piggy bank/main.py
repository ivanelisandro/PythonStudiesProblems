class PiggyBank:
    def __init__(self, dollars, cents):
        self.cents = cents % 100
        self.dollars = dollars + int(cents / 100)

    def add_money(self, deposit_dollars, deposit_cents):
        self.cents += deposit_cents
        if self.cents > 99:
            self.dollars += int(self.cents / 100)
            self.cents = self.cents % 100
        self.dollars += deposit_dollars
