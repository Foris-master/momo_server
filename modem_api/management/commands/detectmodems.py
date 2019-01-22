from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.management import BaseCommand, call_command
from django.db.models import Q

from modem_api.models import Modem, Operator, Service
from modem_api.serializers import ServiceSerializer


class Command(BaseCommand):
    help = "DETECT All Modems and pool informations"

    def handle(self, *args, **options):

        message = {'command': "describe"}

        tools = None

        results = {}

        if Modem.objects.filter(is_active=True).exists():
            results = load_data()

        message['data'] = results


        for modem in Modem.objects.filter(is_active=True).all():
            gn = 'modem_%s' % modem.tag
            channel_layer = get_channel_layer()
            try:
                # pass
                async_to_sync(channel_layer.group_send)(gn, {"type": "chat_message", "message": message})

            except AttributeError as e:
                print(str(e))


def load_data():
    ops = {}
    res = {}
    tags = ['bal', 'phn']
    for operator in Operator.objects.all():
        ops[operator.id] = operator.tag

    queries = [Q(tag__icontains=t) for t in tags]

    # Take one Q object from the list
    query = queries.pop()

    # Or the Q object with the ones remaining in the list
    for item in queries:
        query |= item

    # Query the model

    for service in Service.objects.prefetch_related('answers').filter(query).all():
        s = ServiceSerializer(service).data
        if ops[service.operator_id] not in res:
            res[ops[service.operator_id]] = {'services': {service.tag: s}}
        else:
            res[ops[service.operator_id]]['services'][service.tag] = s
    return res
