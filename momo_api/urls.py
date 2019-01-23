from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from momo_api import views

urlpatterns = [
    path('transactions/', views.TransactionView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', views.TransactionDetail.as_view(), name='transaction-detail'),
    path('proofs/', views.ProofList.as_view(), name='proof-list'),
    path('proofs/<int:pk>/', views.ProofDetail.as_view(), name='proof-detail'),
    path('mobile_wallets/', views.MobileWalletList.as_view(), name='mobile_wallet-list'),
    path('mobile_wallets/<int:pk>/', views.MobileWalletDetail.as_view(), name='mobile_wallet-detail'),
    url(r'^transactions/search/$', views.search_transaction, name='transactions-search'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
