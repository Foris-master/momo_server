from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from modem_api.models import Service, OperatorService, ServiceStation, Station
from modem_api.serializers import OperatorServiceSerializer, StationSerializer, ModemSerializer
from momo_api.models import Transaction


def fill_params(trees, data, res=None):
    if res is None:
        res = {}
    for key, val in trees.items():
        if type(val) is list:
            if key not in res:
                res[key] = []
            for i, val2 in enumerate(val):
                res[key].append(fill_params(val2, data, {}))
        else:
            found = False
            for key2, val2 in data.items():
                if '{' + key2 + '}' == val:
                    res[key] = val2
                    found = True

            if not found:
                res[key] = val
    return res


def proceed_transaction(transaction):
    service1 = Service.objects.filter(tag='sdm2w').first()
    service2 = Service.objects.filter(tag='bal').first()
    op_ser = OperatorService.objects.filter(
        operator=transaction.mobile_wallet.operator,
        service=service1).first()
    data = OperatorServiceSerializer(op_ser).data
    stations = transaction.mobile_wallet.stations
    station = stations.first()
    stations = [station for station in stations.all() if station.state == 'free']
    ss1 = ServiceStation.objects.filter(station=station, service=service2).first()

    for stat in stations:
        ss2 = ServiceStation.objects.filter(station=stat, service=service2).first()
        if ss1.balance < ss2.balance:
            station = stat
            ss1 = ss2
            # avm.append(station)
    data['answer'] = fill_params(data['answer'], {'amount': transaction.amount, 'pin': ss1.pin,
                                                  'phone_number': transaction.recipient})
    # print(data['answer'])
    # for k, v in enumerate(answers):
    #     if v['answer'] == '{pin}':
    #         answers[k]['answer'] = ss1.pin
    #     elif v['answer'] == '{phone_number}':
    #         answers[k]['answer'] = transaction.recipient
    #     elif v['answer'] == '{amount}':
    #         answers[k]['answer'] = transaction.amount
    # data['answers'] = answers

    # send message
    modem = station.modem
    gn = 'modem_%s' % modem.tag
    station.state = 'busy'
    station.save()
    station = StationSerializer(station).data
    message = {
        'transaction': {'amount': transaction.amount, 'is_deposit': transaction.is_deposit,
                        'recipient': transaction.recipient, 'user': transaction.user_id,
                        'mobile_wallet': transaction.mobile_wallet.tag},
        'transaction_id': transaction.id,
        'station_id': station['id'],
        'command': 'proceed_momo',
        'modem': ModemSerializer(modem).data,
        'data': {'station': station, 'service': data}}
    channel_layer = get_channel_layer()
    try:
        # pass
        async_to_sync(channel_layer.group_send)(gn, {"type": "modem_message", "message": message})

    except AttributeError as e:
        print(str(e))


def proceed_transactions():
    transactions = Transaction.objects.filter(status='new').all()
    for transaction in transactions:
        proceed_transaction(transaction)
