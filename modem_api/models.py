from django.db import models

# Create your models here.

from django.db import models
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100, blank=False)
    tag = models.CharField(unique=True, max_length=10)
    ussd = models.CharField(blank=False, max_length=25)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.name


class Answer(models.Model):
    answer = models.CharField(max_length=10, blank=False)
    is_int = models.BooleanField(blank=False, default=False)
    order = models.IntegerField(blank=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='answers')
    description = models.CharField(max_length=20, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return self.answer


class Station(models.Model):
    name = models.CharField(max_length=100, blank=False)
    state = models.CharField(choices=STATION_STATES, default='offline', max_length=100)
    phone_number = models.CharField(validators=[MinLengthValidator(9)], max_length=14, blank=False)
    imei = models.CharField(unique=True, max_length=20)
    imsi = models.CharField(max_length=20)
    port = models.CharField(max_length=10)
    mobile_wallet = models.ForeignKey(Operator, on_delete=models.CASCADE)
    modem = models.ForeignKey(Modem, on_delete=models.CASCADE, null=False, blank=False)
    description = models.TextField(blank=True)
    service_stations = models.ManyToManyField(Service, through='ServiceStation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at',)

    def __str__(self):
        return self.name


class ServiceStation(models.Model):
    balance = models.IntegerField(blank=False, default=0)
    pin = models.CharField(blank=True, max_length=10)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('service', 'station',)
        ordering = ('updated_at',)

    def __str__(self):
        return self.balance
