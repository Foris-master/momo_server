from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.contrib.rest_framework import TokenHasScope, OAuth2Authentication
from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import AccessToken
from rest_framework import generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from modem_api.models import Operator, Station
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


@csrf_exempt
@api_view(('POST',))
@permission_classes(())
@protected_resource(scopes=['modem'])
def prove_transaction(request,version):
    params = request.POST.copy()
    transaction = Transaction.objects.filter(id=params['transaction_id']).get()
    station = Station.objects.filter(imsi=params['station']).get()
    if transaction and station:
        p = Proof.objects.create(
            amount=params['amount'],
            mno_id=params['mno_id'],
            mno_respond=params['mno_respond'],
            station_id=station.id,
            transaction_id=transaction.id
        )
        transaction.status = 'proven'
        transaction.save()
        return Response({'status': 'ok'})
    else:
        return Response({'status': 'not found'})


class TransactionView(APIView):
    authentication_classes = [OAuth2Authentication]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [TokenHasScope]
    required_scopes = []

    def post(self, request, version):
        params = request.POST.copy()
        user = AccessToken.objects.filter(token=request.auth).first().application.user
        params['user'] = user.id

        if 'mobile_wallet' in params and Operator.objects.filter(tag=params['mobile_wallet']).exists():
            op = Operator.objects.filter(tag=params['mobile_wallet']).get()
            if MobileWallet.objects.filter(operator_id=op.id, user_id=user.id).exists():
                mw = MobileWallet.objects.filter(operator_id=op.id, user_id=user.id).get()
                params['mobile_wallet'] = mw.id
            else:
                return Response({'mobile_wallet': 'invalid mobile_wallet'})
        else:
            return Response({'mobile_wallet': 'invalid mobile_wallet'})

        serializer = TransactionSerializer(data=params)
        if serializer.is_valid(raise_exception=True):
            params['amount'] = int(float(params['amount']))
            params['recipient'] = params['recipient'].replace('+237', '')
            print(params['amount'], mw.max_balance, mw.tag)
            if params['amount'] > mw.max_balance:
                return Response({'amount': 'insufficient founds'})
            serializer.save()
            return Response(serializer.data)

    def get(self, request, version):
        print(request.GET)
        user = AccessToken.objects.filter(token=request.auth).first().application.user
        transactions = Transaction.objects.filter(user=user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
