from django.shortcuts import render

# Create your views here.
from oauth2_provider.contrib.rest_framework import TokenHasScope
from rest_framework import generics

from momo_api.filters import TransactionFilter
from momo_api.models import MobileWallet, Transaction, Proof
from momo_api.serializers import MobileWalletSerializer, TransactionSerializer, ProofSerializer


class MobileWalletList(generics.ListCreateAPIView):
    queryset = MobileWallet.objects.all()
    serializer_class = MobileWalletSerializer
    permission_classes = [TokenHasScope]
    required_scopes = ['client']


class MobileWalletDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MobileWallet.objects.all()
    serializer_class = MobileWalletSerializer


class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [TokenHasScope]
    required_scopes = ['client','manager']


class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter
    permission_classes = [TokenHasScope]
    required_scopes = ['client','manager']


class ProofList(generics.ListCreateAPIView):
    queryset = Proof.objects.all()
    serializer_class = ProofSerializer
    permission_classes = [TokenHasScope]
    required_scopes = ['modem']


class ProofDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proof.objects.all()
    serializer_class = ProofSerializer


def search_transaction(request):
    user_list = Transaction.objects.all()
    user_filter = TransactionFilter(request.GET, queryset=user_list)
    return render(request, 'search/user_list.html', {'filter': user_filter})



