import time
import datetime
from application.misc.iex.iex_main import get_all_symbols

current_day = datetime.datetime.utcnow().day


def job1():
    print('Current user sessions')


def job_pseupo_update():
    date = datetime.datetime.utcnow()
    print('data of current pseudo update is [UTC] : ', date)


def job_get_update_all_indexes():
    check_day = datetime.datetime.utcnow().day
    if (check_day != check_day) and (check_day > current_day):  # not today
        print('updating all symbols list')
        get_all_symbols()
    else:
        print('No need to update symbols')
