from django_filters import rest_framework as django_filters

from momo_api.models import Transaction


class TransactionFilter(django_filters.FilterSet):

    amount_gt = django_filters.NumberFilter(name='amount', lookup_expr='gt')
    amount_lt = django_filters.NumberFilter(name='amount', lookup_expr='lt')
    is_deposit = django_filters.CharFilter(lookup_expr='')
    # status = django_filters.CharFilter(lookup_expr='icontains')
    recipient = django_filters.CharFilter(lookup_expr='recipient')
    title = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Transaction
        fields = ['amount', 'track_id', 'is_deposit', 'status', 'recipient', 'user_id',
                  'created_at', 'updated_at']
