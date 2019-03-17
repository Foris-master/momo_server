import json
import os

from django.core.management import BaseCommand, call_command

from modem_api.models import Operator, Service, OperatorService, Answer
from momo_api.consumers import User
from momo_server.settings import BASE_DIR


class Command(BaseCommand):
    help = "DEV COMMAND: Fill databasse with a set of data for testing purposes"

    def handle(self, *args, **options):
        call_command('flush', '--noinput')
        call_command('loaddata', 'groups')
        call_command('loaddata', 'users')
        # Fix the passwords of fixtures
        for user in User.objects.all():
            user.set_password(user.password)
            user.save()
        call_command('loaddata', 'applications', 'modems', 'operators', 'services', 'mobile_wallets')
        self.save_services_answers()

    def save_services_answers(self):
        fp = BASE_DIR + os.sep + 'modem_api' + os.sep + 'fixtures' + os.sep + 'operator_services.json'
        with open(fp) as f:
            datas = json.load(f)
            for data in datas:
                op = Operator.objects.filter(tag=data['operator']).first()
                if op is not None:
                    for service in data['services']:
                        ser = Service.objects.filter(tag=service['service']).first()
                        if ser is not None:

                            if 'entry_answer' in service:
                                tmp_ans = service['entry_answer']
                                p = Answer.objects.create(
                                    answer=tmp_ans['answer'],
                                    is_int=tmp_ans['is_int'],
                                    order=1,
                                    description=tmp_ans['description'],
                                    parent_id=None,
                                )
                                op_ser = OperatorService.objects.create(
                                    ussd=service['ussd'],
                                    operator_id=op.id,
                                    service_id=ser.id,
                                    answer_id=p.id
                                )
                                if 'next' in tmp_ans:
                                    for answer in tmp_ans['next']:
                                        self.save_answers_tree(answer, p.id, 2)

    def save_answers_tree(self, tree, parent=None, ord=1):

        p = Answer.objects.create(
            answer=tree['answer'],
            is_int=tree['is_int'],
            order=ord,
            description=tree['description'],
            parent_id=parent,
        )
        ord += 1
        if 'next' in tree :
            for answer in tree['next']:
                self.save_answers_tree(answer, p.id, ord)
