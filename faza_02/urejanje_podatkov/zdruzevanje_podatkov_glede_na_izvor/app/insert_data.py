from get_data import get_rir_for_ip, IpData
from database_helper import (engine, 
                            add_update_row_ip, 
                            add_update_row_as, 
                            create_tables_if_not_exist,
                            increment_ip_count,
                            ip_in_local_database)

from sqlalchemy.orm import sessionmaker


Session = sessionmaker(bind=engine)
session = Session()

STATUS_OK = 0
STATUS_FAIL = -1
ERROR_BAD_REQUEST = -1
ERROR_NO_DATA = -2


# PREVERIMO ALI TABELE OBSTAJAJO, ČE NE JIH USTVARIMO
create_tables_if_not_exist(engine)

def get_data_for_ip(rir, ip):
    ip_data = IpData(rir, ip)
    ip_data.get_data()

    if ip_data.status in (STATUS_FAIL, ERROR_NO_DATA, ERROR_NO_DATA):
        pass
    else:
        add_update_row_as(session, ip_data)
        add_update_row_ip(session, ip_data)
        pass
        
def parse_ips(ips):
    i = 1
    num_of_ip = len(ips)
    for ip in ips:
        # PREVERIMO ALI IP OBSTAJA V LOKALNI BAZI IN GA POVEČAMO ZA 1
        print(i, '/', num_of_ip, ': Checking ip', ip, '...')
        i = i + 1
        if ip_in_local_database(session, ip):
            increment_ip_count(session, ip)
            print('IP in local DB.')
        else:
            rir = get_rir_for_ip(ip)
            if rir in ('RIPE NCC', 'ARIN', 'APNIC', 'LACNIC', 'AFRINIC'):
                get_data_for_ip(rir, ip)
                print('RIR: ', rir)  
            else:
                print('ERROR: no rir info')
                print(rir)
              
        print('-------------')


