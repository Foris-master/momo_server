import os

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from twilio.rest import Client
from django.template.loader import render_to_string

dformat = "%A %d %h %Y  %Hh %Mmin %S seconds"


def send_sms(to, message):
    '''sms utility method'''

    client = Client(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    response = client.messages.create(
        body=message, to=to, from_=os.getenv("TWILIO_FROM"))
    return response


def send_many_sms(recipients):
    for recipient in recipients:
        send_sms(recipient['number'], recipient['message'])


def send_modem_state_email(modem):
    body = 'The modem named ' + modem.name + ' is offline please check it ( internet connection ; electricity ' \
                                             '; websocket client) '

    users = Group.objects.filter(name='manager').get().user_set
    recipients = list(i for i in users.values_list('email', flat=True) if bool(i))
    state = 'ONLINE' if modem.is_active else 'OFFLINE'
    content = {
        "modem": modem.name,
        "state": state,
        "is_online": modem.is_active,
        "when": datetime.now().strftime(dformat)
    }
    html_content = render_to_string('email/modem_state.html', content)
    text_content = strip_tags(html_content)

    subject = 'Modem ' + modem.name + ' ( ' + modem.tag + ' ) is ' + state + ' (please check) !!!'
    email = EmailMultiAlternatives(subject,
                                   text_content,
                                   to=recipients)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print('email send')
    # send_mail(
    #     'Modem ' + modem.name + ' ( '+modem.tag+' ) is offline (please check) !!!',
    #     body,
    #     recipient_list=['evarisfomekong@gmail.com'],
    #     fail_silently=False,
    # )


def send_modem_state_sms(modem):
    template = 'sms/modem_state.html'
    users = Group.objects.filter(name='manager').get().user_set.all()
    recipients = []
    from modem_api.models import Profile
    for user in users:

        if type(user.profile) is Profile:
            r = {'number': user.profile.phone_number.as_international}
            content = {
                "modem": modem.name,
                "name": user.get_full_name(),
                "is_online": modem.is_active,
                "when": datetime.now().strftime(dformat)
            }

            message = render_to_string(template, content)
            message = message.encode('utf-8')
            r['message'] = message
            recipients.append(r)
    send_many_sms(recipients)
