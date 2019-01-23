from django.db import models

# Create your models here.

from django.db import models
from django.db.models.signals import post_init
from fernet_fields import EncryptedCharField
from rest_framework.compat import MinLengthValidator

STATION_STATES = [('free', 'FREE'), ('busy', 'BUSY'), ('offline', 'OFFLINE')]


class Modem(models.Model):
    name = models.CharField(max_length=100, blank=False)
    tag = models.CharField(unique=True, max_length=10)
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.name


class Operator(models.Model):
    name = models.CharField(max_length=100, blank=False)
    tag = models.CharField(unique=True, max_length=10)
    country = models.CharField(max_length=100)
    description = models.TextField()
    service_stations = models.ManyToManyField('Service', through='OperatorService')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100, blank=False)
    tag = models.CharField(unique=True, max_length=10)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    service_stations = models.ManyToManyField(Operator, through='OperatorService')

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.name


class OperatorService(models.Model):
    ussd = models.CharField(blank=False, max_length=25)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='operator_services')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)
        unique_together = ('service', 'operator',)

    def __str__(self):
        return self.operator.name + ' ' + self.service.name + ' ' + self.ussd


class Answer(models.Model):
    answer = models.CharField(max_length=20, blank=False)
    is_int = models.BooleanField(blank=False, default=False)
    order = models.IntegerField(blank=False)
    operator_service = models.ForeignKey(OperatorService, on_delete=models.CASCADE, related_name='answers')
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order',)
        unique_together = ('order', 'operator_service',)

    def __str__(self):
        return self.answer


class Station(models.Model):
    name = models.CharField(max_length=100, blank=False)
    state = models.CharField(choices=STATION_STATES, default='offline', max_length=100)
    phone_number = models.CharField(validators=[MinLengthValidator(9)], max_length=14, blank=False)
    imei = models.CharField(unique=True, max_length=20)
    imsi = models.CharField(max_length=20)
    port = models.CharField(max_length=10)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    modem = models.ForeignKey(Modem, on_delete=models.CASCADE, null=False, blank=False, related_name='stations')
    description = models.TextField(blank=True)
    services = models.ManyToManyField(Service, through='ServiceStation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)
        unique_together = ('phone_number', 'modem',)

    def __str__(self):
        return self.name


class ServiceStation(models.Model):
    balance = models.IntegerField(blank=False, default=0)
    pin = EncryptedCharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='service_stations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('service', 'station',)
        ordering = ('updated_at',)

    def __str__(self):
        return self.service.name + " " + self.station.name + " " + str(self.balance)

    @staticmethod
    def remember_state(sender, **kwargs):
        instance = kwargs.get('instance')
        instance.previous_balance = instance.balance


post_init.connect(ServiceStation.remember_state, sender=ServiceStation)
