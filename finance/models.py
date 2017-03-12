from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    KIND_CHOICES = [
        ('BANK', 'Bank Account'),
        ('CREDITCARD', 'Credit Card'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    kind = models.CharField(max_length=50, choices=KIND_CHOICES, default='BANK')
    bank_id = models.CharField(blank=True, max_length=100)
    account_id = models.CharField(blank=True, max_length=100)
    starting_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'bank_id', 'account_id')

    def __str__(self):
        return f'{self.user}/{self.account_id}'

    @property
    def balance(self):
        return self.starting_balance + sum(row['amount'] for row in self.transaction_set.values('amount'))


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
