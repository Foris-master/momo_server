from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.compat import MinLengthValidator

from modem_api.models import Operator, Station, ServiceStation, Service

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


@receiver(post_save, sender=ServiceStation)
def ensure_balance_correct(sender, **kwargs):
    print(kwargs)
    ss = kwargs.get('instance')
    print(ss.balance)
    print(ss.previous_balance)
    mw = MobileWallet.objects.filter(operator=ss.station.operator).first()
    if kwargs.get('created', False):
        mw.balance += ss.balance
    else:
        mw.balance -= ss.previous_balance
        mw.balance += ss.balance
    if ss.balance > mw.max_balance:
        mw.max_balance = ss.balance
    mw.save()


class Transaction(models.Model):
    amount = models.IntegerField(blank=False)
    track_id = models.CharField(blank=False, unique=True, max_length=20)
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

@receiver(post_save, sender=Transaction)
def proceed_transaction(sender, **kwargs):

    transaction = kwargs.get('instance')

    service = Service.objects.filter(operator=transaction.mobile_wallet.operator).first()

    stations = transaction.mobile_wallet.stations
    avm = []
    for station in stations:
        if station.modem.is_active:
            avm.append(station)
    if kwargs.get('created', False):
        pass
    else:
        pass




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
