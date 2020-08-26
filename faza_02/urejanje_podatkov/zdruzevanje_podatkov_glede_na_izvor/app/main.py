#!/usr/bin/env python3

from database_helper import engine
from sqlalchemy.orm import sessionmaker
import datetime
import configparser


from insert_data import parse_ips

Session = sessionmaker(bind=engine)
session = Session()


def get_round_times(dt=None, date_delta=datetime.timedelta(minutes=10), to='down', interval=10):
    """
    Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 10 minutes.
    """
    round_to = date_delta.total_seconds()
    if dt is None:
        dt = datetime.datetime.now()

    seconds = (dt - dt.min).seconds

    if seconds % round_to == 0:
        rounding = (seconds + round_to / 2) // round_to * round_to
    else:
        if to == 'up':
            rounding = (seconds + round_to) // round_to * round_to
        elif to == 'down':
            rounding = seconds // round_to * round_to
        else:
            rounding = (seconds + round_to / 2) // round_to * round_to

    time = dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)

    time_start = time - datetime.timedelta(minutes=interval) - datetime.timedelta(minutes=10)
    time_start = time_start.strftime('%Y-%m-%d %H:%M:%S')

    time_end = time - datetime.timedelta(minutes=10)
    time_end = time_end.strftime('%Y-%m-%d %H:%M:%S')

    return (time_start, time_end)

def get_ips(start_time_, end_time_, table_name):
    print('get_ips function')
    ips = []
    query = 'SELECT src_ip FROM ' + table_name + ' where connect_timestamp >= "' + start_time_ + '" and connect_timestamp < "' + end_time_ + '";'
    # query = 'SELECT src_ip FROM ' + table_name + ' LIMIT 8;'

    print(query)
    with engine.connect() as con:
        print(con)
        ip_row = con.execute(query)
        print(ip_row)

    for ip in ip_row:
        ips.append(ip[0])

    ips = list(ips) 
    print(ips)   
    return ips

def filter_ips(ips):
    print('filter_ips')
    ips_filtered = list()
    for ip in ips:
        if (ip.startswith('10.') or ip.startswith('192.168.')):
            continue
        elif ip == '212.235.185.131': # Filter LTFE IPs
            continue
        else:
            ips_filtered.append(ip)
    return ips_filtered



config = configparser.ConfigParser(allow_no_value=True)
config.read('./app/provider_analyzer.conf')

all_data_table_name = str(config['DB_READ']['ALL_TABLE_NAME'])


def run_analisys(time_start, time_end):
    print('Getting ips: ')
    ips = get_ips(time_start, time_end, all_data_table_name)
    ips = filter_ips(ips)
    parse_ips(ips)


def realtime():
    t_start, t_end = get_round_times(date_delta=datetime.timedelta(minutes=10), to='down', interval=10)
    time_string = f'Start: {t_start} -> End: {t_end}'

    with open('./time_inserts.log', 'r') as f:
        if time_string in f.read():
            inserted = True
        else:
            inserted = False

    if not inserted:
        print(f'[{time_string}] Analizing interval for providers.')
        with open('./time_inserts.log', 'a') as f_append:
            f_append.write(time_string+'\n')
        run_analisys(t_start, t_end)
    else:
        print(f'[{time_string}] Interval already analized.')


def normal_mode():
    start_time_string = '2019-12-01 00:00:00'
    end_time_string = '2019-12-01 23:59:59'

    print(f'Start: {start_time_string} -> End: {end_time_string}')

    run_analisys(start_time_string, end_time_string)

realtime()        
#normal_mode()
