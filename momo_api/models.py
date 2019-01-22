from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from rest_framework.compat import MinLengthValidator

from modem_api.models import Operator, Station

TRANSACTION_STATUSES = [('new', 'NEW'), ('pending', 'PENDING'), ('paid', 'PAID'), ('cancel', 'CANCEL')]


class MobileWallet(models.Model):
    name = models.CharField(max_length=100)
    tag = models.CharField(unique=True, max_length=10)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    balance = models.IntegerField(blank=False)
    max_balance = models.IntegerField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    amount = models.IntegerField(blank=False)
    track_id = models.CharField(blank=True, unique=True, max_length=20)
    is_deposit = models.BooleanField(default=True)
    status = models.CharField(choices=TRANSACTION_STATUSES, default='new', max_length=100)
    recipient = models.CharField(validators=[MinLengthValidator(9)], max_length=14)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile_wallet = models.ForeignKey(MobileWallet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.amount


class Proof(models.Model):
    amount = models.IntegerField(blank=False)
    mno_id = models.CharField(blank=False, max_length=100)
    mno_respond = models.CharField(blank=False, max_length=100)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.amount
