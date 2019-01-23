from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

# from .models import Message, Chat, Contact
# from .views import get_last_10_messages, get_user_contact, get_current_chat
from modem_api.models import Modem, Station, Operator, ServiceStation, Service

User = get_user_model()


class ModemConsumer(WebsocketConsumer):

    # def fetch_messages(self, data):
    #     messages = get_last_10_messages(data['chatId'])
    #     content = {
    #         'command': 'messages',
    #         'messages': self.messages_to_json(messages)
    #     }
    #     self.send_message(content)
    #
    # def new_message(self, data):
    #     user_contact = get_user_contact(data['from'])
    #     message = Message.objects.create(
    #         contact=user_contact,
    #         content=data['message'])
    #     current_chat = get_current_chat(data['chatId'])
    #     current_chat.messages.add(message)
    #     current_chat.save()
    #     content = {
    #         'command': 'new_message',
    #         'message': self.message_to_json(message)
    #     }
    #     return self.send_chat_message(content)
    #
    # def messages_to_json(self, messages):
    #     result = []
    #     for message in messages:
    #         result.append(self.message_to_json(message))
    #     return result
    #
    # def message_to_json(self, message):
    #     return {
    #         'id': message.id,
    #         'author': message.contact.user.username,
    #         'content': message.content,
    #         'timestamp': str(message.timestamp)
    #     }
    #

    def update_modem(self, response):
        print(response['data'])
        for (port, dat) in response['data'].items():
            ph = dat['phone_number']
            op = Operator.objects.filter(tag=dat['operator']).first()
            if not Station.objects.filter(phone_number=ph).exists():
                station = Station()
            else:
                station = Station.objects.filter(phone_number=ph).first()
                if 'balance' in dat and dat['balance']['value'] is not None:
                    service = Service.objects.filter(tag=dat['balance']['service']).first()
                    ss = ServiceStation.objects.filter(station=station, service=service).first()
                    b = dat['balance']['value']
                    b= b.replace(',','')
                    ss.balance = int(float(b))
                    ss.save()

            station.name = ph
            station.state = 'new'
            station.phone_number = ph
            station.imei = dat['imei']
            station.imsi = dat['imsi']
            station.port = port

            station.description = str({
                'network': dat['network'],
                'signal': dat['signal'],
                'manufacturer': dat['manufacturer'],
                'model': dat['model'],
                'alive': dat['alive']
            })

            station.modem_id = self.modem.id
            station.operator_id = op.id
            station.save()

    def proceed_momo(self, response):
        print(response['data'])
        for (port, dat) in response['data'].items():
            ph = dat['phone_number']
            op = Operator.objects.filter(tag=dat['operator']).first()
            if not Station.objects.filter(phone_number=ph).exists():
                station = Station()
            else:
                station = Station.objects.filter(phone_number=ph).first()
                if 'balance' in dat and dat['balance']['value'] is not None:
                    service = Service.objects.filter(tag=dat['balance']['service']).first()
                    ss = ServiceStation.objects.filter(station=station, service=service).first()
                    b = dat['balance']['value']
                    b= b.replace(',','')
                    ss.balance = int(float(b))
                    ss.save()

            station.name = ph
            station.state = 'new'
            station.phone_number = ph
            station.imei = dat['imei']
            station.imsi = dat['imsi']
            station.port = port

            station.description = str({
                'network': dat['network'],
                'signal': dat['signal'],
                'manufacturer': dat['manufacturer'],
                'model': dat['model'],
                'alive': dat['alive']
            })

            station.modem_id = self.modem.id
            station.operator_id = op.id
            station.save()

    commands = {
        'describe': update_modem,
        'proceed_momo': proceed_momo,
    }

    def change_modem_state(self, tag, state=True):
        print(tag)
        self.modem = Modem.objects.filter(tag=tag).first()

        if self.modem is not None:
            print(state)
            self.modem.is_active = state
            self.modem.save()

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['tag']
        self.room_group_name = 'modem_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.change_modem_state(self.room_name)

        self.accept()

    def disconnect(self, close_code):
        self.change_modem_state(self.room_name, False)
        print("connection closed" + self.room_group_name)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        # print(str(text_data))
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
