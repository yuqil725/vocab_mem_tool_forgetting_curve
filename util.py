from datetime import datetime, timedelta


def datetime_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def datetime_after_now(seconds = 0):
    return (datetime.now()+ timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S')

def cmp_date(ds1, ds2):
    return datetime.strptime(ds1, '%Y-%m-%d %H:%M:%S') > datetime.strptime(ds2, '%Y-%m-%d %H:%M:%S')