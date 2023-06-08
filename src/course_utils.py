import os

data_dir = os.path.abspath(os.getcwd() + "/../../")
data_dir = "/home/shardwic/github/nlp-tools/vrt/"

import datetime

def month_range(start_date, end_date):
    '''Given start_date and end_date (of type datetime.date), return
    a list of dates representing the first days of every month overlapping
    their range.'''
    months = []
    month = start_date.replace(day=1)
    while month <= end_date:
        months.append(month)
        month = (month + datetime.timedelta(days=40)).replace(day=1)
    return months
