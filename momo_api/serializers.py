from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Proof, MobileWallet, Transaction


class ProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proof
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    # mobile_wallet = serializers.RelatedField(source=MobileWallet, read_only=True)
    # user = serializers.RelatedField(source=User, read_only=True)
    # proofs = ProofSerializer(many=True)

    class Meta:
        model = Transaction
        # fields = ('__all__')
        fields = (
            'id', 'amount', 'track_id', 'status', 'recipient', 'mobile_wallet', 'user', 'created_at', 'updated_at')


class MobileWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileWallet
        fields = '__all__'
