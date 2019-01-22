from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Modem, Operator, Answer, Service, ServiceStation, Station


class ModemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modem
        fields = ('id', 'name', 'tag', 'description', 'is_active', 'created_at', 'updated_at')


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ('id', 'tag', 'ussd','answers')


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class ServiceStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStation
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)
