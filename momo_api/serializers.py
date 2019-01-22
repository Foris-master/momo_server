from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Transaction, Proof, MobileWallet


class ProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proof
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'name', 'tag', 'description', 'is_active', 'created_at', 'updated_at')
        proofs = ProofSerializer(many=True)


class MobileWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileWallet
        fields = '__all__'
