import datetime

from django.contrib.auth.models import User
from django.db import models


class BalanceMixin:
    @property
    def balance(self):
        return self.starting_balance + sum(row['amount'] for row in self.transaction_set.values('amount'))

    def balance_up_to(self, date):
        return self.starting_balance + sum(row['amount'] for row in self.transaction_set.filter(date_posted__lte=date).values('amount'))

    @property
    def balance_history(self):
        results = []

        today = datetime.date.today()

        for i in range(78):
            balance = self.balance_up_to(today)
            results.append((today, balance))

            today -= datetime.timedelta(weeks=1)

        return sorted(results, key=lambda x: x[0])


class SpendingMixin:

    def transactions_for(self, start, finish):
        return self.transaction_set.filter(date_posted__gt=start, date_posted__lte=finish)

    def income_for(self, start, finish):
        transactions = self.transactions_for(start, finish).filter(amount__gt=0)
        return sum(t.amount for t in transactions)

    def spending_for(self, start, finish):
        transactions = self.transactions_for(start, finish).filter(amount__lt=0)
        return sum(t.amount for t in transactions)

    @property
    def spending_history(self):
        results = []

        today = datetime.date.today()

        for i in range(18):
            next_today = today.replace(day=1) - datetime.timedelta(days=1)

            income = self.income_for(next_today, today)
            spending = self.spending_for(next_today, today)
            results.append((today, income, spending))

            today = next_today

        return sorted(results, key=lambda x: x[0])


class Profile(models.Model, BalanceMixin, SpendingMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def starting_balance(self):
        return sum(a.starting_balance for a in self.account_set.all())


class Account(models.Model, BalanceMixin, SpendingMixin):
    KIND_CHOICES = [
        ('BANK', 'Bank Account'),
        ('CREDITCARD', 'Credit Card'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    kind = models.CharField(max_length=50, choices=KIND_CHOICES, default='BANK')
    bank_id = models.CharField(blank=True, max_length=100)
    account_id = models.CharField(blank=True, max_length=100)
    starting_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        unique_together = ('profile', 'bank_id', 'account_id')

    def __str__(self):
        return f'{self.profile}/{self.name}'

    @property
    def name(self):
        return f'{self.kind} - {self.account_id}'

    @property
    def colour(self):
        colours = [
            'rgb(26, 188, 156)',
            'rgb(52, 152, 219)',
            'rgb(142, 68, 173)',
        ]

        return colours[self.id % len(colours)]


class Transaction(models.Model):
    KIND_CHOICES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
        ('INT', 'Interest'),
        ('DIV', 'Dividend'),
        ('FEE', 'FI Fee'),
        ('SRVCHG', 'Service Charge'),
        ('DEP', 'Deposit'),
        ('ATM', 'ATM'),
        ('POS', 'Point of Sale'),
        ('XFER', 'Transfer'),
        ('CHECK', 'Check'),
        ('PAYMENT', 'Electronic Payment'),
        ('CASH', 'Cash Withdrawal'),
        ('DIRECTDEP', 'Direct Deposit'),
        ('DIRECTDEBIT', 'Direct Debit'),
        ('REPEATPMT', 'Repeating Payment'),
        ('HOLD', 'Hold'),
        ('OTHER', 'Other'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    transaction_id = models.TextField()
    date_posted = models.DateField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    kind = models.CharField(max_length=25, choices=KIND_CHOICES)
    name = models.TextField()

    class Meta:
        unique_together = ('account', 'transaction_id')

    def __str__(self):
        return f'{self.account} {self.date_posted} {self.name} {self.amount}'
