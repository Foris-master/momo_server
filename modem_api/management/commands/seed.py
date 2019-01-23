from django.core.management import BaseCommand, call_command

from momo_api.consumers import User


class Command(BaseCommand):
    help = "DEV COMMAND: Fill databasse with a set of data for testing purposes"

    def handle(self, *args, **options):
        call_command('flush','--noinput')
        call_command('loaddata', 'groups')
        call_command('loaddata', 'users')
        # Fix the passwords of fixtures
        for user in User.objects.all():
            user.set_password(user.password)
            user.save()
        call_command('loaddata', 'applications', 'modems', 'operators', 'services', 'operator_services', 'mobile_wallets', 'answers')
