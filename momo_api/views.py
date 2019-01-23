from django.shortcuts import render

# Create your views here.
from oauth2_provider.contrib.rest_framework import TokenHasScope, OAuth2Authentication
from oauth2_provider.models import AccessToken
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

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
    required_scopes = []


class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter
    permission_classes = [TokenHasScope]
    required_scopes = ['client', 'manager', 'modem']


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


class TransactionView(APIView):
    authentication_classes = [OAuth2Authentication]
    # serializer_class = TransactionSerializer
    permission_classes = [TokenHasScope]
    required_scopes = []

    def post(self, request):
        params = request.POST.copy()
        user = AccessToken.objects.filter(token=request.auth).first().application.user
        params['user'] = user.id

        if 'mobile_wallet' in params and MobileWallet.objects.filter(tag=params['mobile_wallet']).exists():
            mw = MobileWallet.objects.filter(tag=params['mobile_wallet']).first()
            params['mobile_wallet'] = mw.id
        else:
            return Response({'mobile_wallet': 'invalid mobile_wallet'})

        serializer = TransactionSerializer(data=params)
        if serializer.is_valid(raise_exception=True):
            if int(params['amount']) > mw.max_balance:
                return Response({'amount': 'insufficient founds'})
            serializer.save()
            return Response(serializer.data)
