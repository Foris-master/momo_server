import difflib
from time import time

from django_cron import CronJobBase, Schedule

from momo_api.lib import proceed_transactions


class ProceedTransactionJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every 5 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'momo_server.fetch_stations'  # a unique code

    def do(self):
        start = time()
        proceed_transactions()
        finish = time()
        t = (finish - start)
        print('time ' + str(t))
