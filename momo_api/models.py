import pprint

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import models

# Create your models here.
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from rest_framework.compat import MinLengthValidator

from modem_api.models import Operator, Station, ServiceStation, Service, OperatorService
from modem_api.serializers import OperatorServiceSerializer, StationSerializer, ModemSerializer


TRANSACTION_STATUSES = [('new', 'NEW'), ('pending', 'PENDING'), ('paid', 'PAID'), ('proven', 'PROVEN'),
                        ('cancel', 'CANCEL')]


class MobileWallet(models.Model):
    name = models.CharField(max_length=100)
    tag = models.CharField(unique=True, max_length=10)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    balance = models.IntegerField(blank=False)
    max_balance = models.IntegerField(blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stations = models.ManyToManyField(Station, related_name='mobilewallets', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.name


def sync_mobile_wallet_balance(mw):
    mw.balance = 0
    mw.max_balance = 0
    service = Service.objects.filter(tag='bal').get()
    for station in mw.stations.all():
        ss = ServiceStation.objects.filter(service=service, station=station).get()
        if ss.balance > mw.max_balance:
            mw.max_balance = ss.balance
        mw.balance += ss.balance
    mw.save()


@receiver(m2m_changed, sender=MobileWallet.stations.through)
def ensure_mobile_wallet_balance_correct_stations(sender, **kwargs):
    # print(kwargs)
    mw = kwargs.get('instance')
    sync_mobile_wallet_balance(mw)


@receiver(post_save, sender=ServiceStation)
def ensure_balance_correct(sender, **kwargs):
    # print(kwargs)
    ss = kwargs.get('instance')
    for mw in ss.station.mobilewallets.all():
        sync_mobile_wallet_balance(mw)
        # mw = MobileWallet.objects.filter(operator=ss.station.operator).first()
        # if kwargs.get('created'):
        #     mw.balance += ss.balance
        # else:
        #     mw.balance -= ss.previous_balance
        #     mw.balance += ss.balance
        # if ss.balance > mw.max_balance:
        #     mw.max_balance = ss.balance
        # mw.save()
    if kwargs.get('created'):
        call_command('detectmodems', '--modem_tag', ss.station.modem.tag)


@receiver(post_delete, sender=ServiceStation)
def ensure_balance_correct_delete(sender, **kwargs):
    # print(kwargs)
    ss = kwargs.get('instance')
    for mw in ss.station.mobilewallets.all():
        # mw = MobileWallet.objects.filter(operator=ss.station.operator).first()
        # mw.balance -= ss.balance
        # mw.save()
        sync_mobile_wallet_balance(mw)


class Transaction(models.Model):
    amount = models.IntegerField(blank=False)
    track_id = models.CharField(blank=False, unique=True, max_length=20)
    is_deposit = models.BooleanField(default=True)
    recipient_has_wallet = models.BooleanField(default=True)
    status = models.CharField(choices=TRANSACTION_STATUSES, default='new', max_length=100)
    recipient = models.CharField(validators=[MinLengthValidator(9)], max_length=14)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile_wallet = models.ForeignKey(MobileWallet, on_delete=models.CASCADE)
    recipient_operator = models.ForeignKey(Operator, on_delete=models.CASCADE, null=True, blank=True)
    history = models.CharField(null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return str(self.amount) + ' FCFA ' + self.status


@receiver(post_save, sender=Transaction)
def proceed_transaction(sender, **kwargs):
    transaction = kwargs.get('instance')

    if kwargs.get('created', False):
        if transaction.status == 'paid' or transaction.status == 'proven':
            try:

                # url = url + 'oauth/token/'
                url = transaction.user.oauth2_provider_application.first().redirect_uris
                dat = {
                    'id': transaction.id,
                    'amount': transaction.amount,
                    'track_id': transaction.track_id,
                    'status': transaction.status,
                    'recipient': transaction.recipient,
                    'mobile_wallet': transaction.mobile_wallet.operator.tag,
                    'created_at': transaction.created_at,
                    'updated_at': transaction.updated_at
                }
                if type(url) is not str:
                    r = requests.post(
                        url,
                        data=dat,
                    )
                    print(r.json())

            except ConnectionError as ex:
                print(ex)
            except Exception as ex:
                print(ex)
    else:
        pass


class Proof(models.Model):
    amount = models.IntegerField(blank=False)
    mno_id = models.CharField(blank=False, max_length=100)
    mno_respond = models.CharField(blank=False, max_length=255)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return str(self.amount)
