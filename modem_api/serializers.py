from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Modem, Operator, Answer, Service, ServiceStation, Station, OperatorService


class ServiceStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStation
        fields = ('id', 'pin', 'balance', 'created_at', 'updated_at')


class StationSerializer(serializers.ModelSerializer):
    service_stations = ServiceStationSerializer(many=True, read_only=True)

    class Meta:
        model = Station
        fields = (
            'id', 'name', 'state', 'phone_number', 'imei', 'imsi', 'port', 'description', 'service_stations',
            'created_at', 'updated_at')


class ModemSerializer(serializers.ModelSerializer):
    stations = StationSerializer(many=True, read_only=True)

    class Meta:
        model = Modem
        fields = ('id', 'name', 'tag', 'description', 'is_active', 'stations', 'created_at', 'updated_at')


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class AnswerSerializer(serializers.ModelSerializer):
    # next_answers= AnswerSerializer(many=True, read_only=True)
    next_answers = RecursiveSerializer(many=True, read_only=True)
    class Meta:
        model = Answer
        fields = ('id','answer','is_int','order','description','next_answers')


class OperatorServiceSerializer(serializers.ModelSerializer):
    # answers = AnswerSerializer(many=True, read_only=True)
    answer = AnswerSerializer(read_only=True)
    class Meta:
        model = OperatorService
        fields = ('id', 'operator', 'ussd', 'answer')


class ServiceSerializer(serializers.ModelSerializer):
    operator_services = OperatorServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ('id', 'name', 'tag', 'operator_services')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)
        extra_kwargs = {
            'password': {'write_only': True}
        }
