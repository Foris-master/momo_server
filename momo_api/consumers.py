from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

# from .models import Message, Chat, Contact
# from .views import get_last_10_messages, get_user_contact, get_current_chat
from modem_api.models import Modem

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
    # commands = {
    #     'fetch_messages': fetch_messages,
    #     'new_message': new_message
    # }

    def change_modem_state(self, tag, state=True):
        print(tag)
        self.modem = Modem.objects.filter(tag=tag).first()

        if self.modem is not None:
            self.modem.is_active=state
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
        self.change_modem_state(self.room_name,False)
        print("connection closed" + self.room_group_name)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # data = json.loads(text_data)
        print(str(text_data))
        # self.commands[data['command']](self, data)

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