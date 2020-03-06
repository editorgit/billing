from djmoney.models.fields import MoneyField

from django.contrib.auth.models import User
from django.db import models


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    balance = MoneyField(max_digits=10, decimal_places=2, default=0, default_currency='EUR')
    last_changed_at = models.DateTimeField(auto_now=True, auto_created=True)

    class Meta:
        db_table = 'wallet'

    def __str__(self):
        return f"{self.user}: {self.balance}"


class MoneyConversion(models.Model):
    initial_currency = models.CharField(max_length=3)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=5)
    converted_currency = models.CharField(max_length=3)
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, auto_created=True)

    class Meta:
        db_table = 'conversions'

    def __str__(self):
        return f"{self.initial_amount}{self.initial_currency}>" \
               f"{self.converted_amount}{self.converted_currency}"


class MoneyTransfer(models.Model):
    sender = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING, related_name='senders')
    receiver = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING, related_name='receivers')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    converter = models.ForeignKey(MoneyConversion, on_delete=models.DO_NOTHING, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_created=True)

    class Meta:
        db_table = 'transfers'

    def __str__(self):
        convert = True if self.converter else False
        return f"{self.sender} -> {self.receiver} " \
               f"Is convert: {convert} at {self.created_at}"
