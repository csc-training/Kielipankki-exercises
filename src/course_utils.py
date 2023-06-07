import os

data_dir = os.path.abspath(os.getcwd() + "/../../")


import datetime

def increment_month(date):
    return (date.replace(day=1) + datetime.timedelta(days=40)).replace(day=1)
