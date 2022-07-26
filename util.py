from datetime import datetime, timedelta
import time


def datetime_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def datetime_after_now(seconds = 0):
    return (datetime.now()+ timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S')

def cmp_date(ds1: str, ds2: str):
    return datetime.strptime(ds1, '%Y-%m-%d %H:%M:%S') > datetime.strptime(ds2, '%Y-%m-%d %H:%M:%S')

def datetime_str_to_ts(ds: str):
    return time.mktime(datetime.strptime(ds, '%Y-%m-%d %H:%M:%S').timetuple())

def datetime_dff(ds1: str, ds2: str):
    return datetime_str_to_ts(ds1) - datetime_str_to_ts(ds2)