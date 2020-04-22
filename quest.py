from datetime import datetime, date, timedelta
from chinese_calendar import is_workday
import os
import sys
import yaml


def get_date_list(start_date):
    travel = []
    for i in range(0, DAYS + 1):
        travel.append(str(start_date + timedelta(days=i)))
    return travel


path = sys.path[0]
with open(path + '/setting.yml', encoding='utf-8') as f:
    setting = yaml.load(f, yaml.FullLoader)
    YEAR = setting['travel']['year']
    MONTH = setting['travel']['month']
    DAY = setting['travel']['day']
    DAYS = setting['travel']['days']

today = date.today()


def execute_kq():
    if is_workday(today) and str(today) not in get_date_list(datetime(YEAR, MONTH, DAY).date()):
        os.system('python main.py')


if __name__ == '__main__':
    execute_kq()
