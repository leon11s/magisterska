from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean

import configparser

config = configparser.ConfigParser(allow_no_value=True)
config.read('./cowrie-data-extractor.conf')

TABLE_NAME = str(config['OUTPUTS_DB']['TABLE_NAME'])
dialect = str(config['OUTPUTS_DB']['dialect'])
user = str(config['OUTPUTS_DB']['user'])
password = str(config['OUTPUTS_DB']['password'])
host = str(config['OUTPUTS_DB']['host'])
dbname = str(config['OUTPUTS_DB']['dbname'])

## CONFIG FOR ADDING ROWS IN THE TABLE
insert_in_table_node_name = config.getboolean('TABLES_COLUMNS', 'node_name') 
insert_in_table_session = config.getboolean('TABLES_COLUMNS', 'session') 
insert_in_table_event_counter = config.getboolean('TABLES_COLUMNS', 'event_counter')
insert_in_table_src_ip = config.getboolean('TABLES_COLUMNS', 'src_ip')
insert_in_table_protocol = config.getboolean('TABLES_COLUMNS', 'protocol')
insert_in_table_dst_port = config.getboolean('TABLES_COLUMNS', 'dst_port')
insert_in_table_dst_ip = config.getboolean('TABLES_COLUMNS', 'dst_ip')
insert_in_table_src_port = config.getboolean('TABLES_COLUMNS', 'src_port')
insert_in_table_sensor = config.getboolean('TABLES_COLUMNS', 'sensor')
insert_in_table_connect_timestamp = config.getboolean('TABLES_COLUMNS', 'connect_timestamp')
insert_in_table_country_name = config.getboolean('TABLES_COLUMNS', 'country_name')
insert_in_table_location_lon = config.getboolean('TABLES_COLUMNS', 'location_lon')
insert_in_table_location_lat = config.getboolean('TABLES_COLUMNS', 'location_lat')
insert_in_table_closed_timestamp = config.getboolean('TABLES_COLUMNS', 'closed_timestamp')
insert_in_table_duration = config.getboolean('TABLES_COLUMNS', 'duration')
insert_in_table_arch = config.getboolean('TABLES_COLUMNS', 'arch')
insert_in_table_file_downloaded = config.getboolean('TABLES_COLUMNS', 'file_downloaded')
insert_in_table_per_event_statistic = config.getboolean('TABLES_COLUMNS', 'per_event_statistic')
insert_in_table_login_statistics = config.getboolean('TABLES_COLUMNS', 'login_statistics')
insert_in_table_command_statistics = config.getboolean('TABLES_COLUMNS', 'command_statistics')

cowrie_login_data_table_name = str(config['TABLES_CREATE']['cowrie_login_data_table_name'])
create_cowrie_login_data_table = config.getboolean('TABLES_CREATE', 'create_cowrie_login_data_table')

cowrie_commands_data_table_name = str(config['TABLES_CREATE']['cowrie_commands_data_table_name'])
create_cowrie_commands_data_table = config.getboolean('TABLES_CREATE', 'create_cowrie_commands_data_table')

if dialect == 'sqlite':
    url = dialect + ':///' + dbname
else:
    url = dialect + '://' + user + ':' + password + '@' + host + '/' + dbname

print('Creating table with:', url)

engine = create_engine(url, echo=False)
Base = declarative_base()

if create_cowrie_login_data_table:
    print('Creating table:', cowrie_login_data_table_name)
    class CowrieLoginData(Base):
        __tablename__ = cowrie_login_data_table_name

        id = Column(Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
        sensor = Column(String(50))
        node_name = Column(String(30))
        session = Column(String(15))
        username = Column(String(100))
        password = Column(String(100))
        login_tries = Column(Integer)
        success = Column(Boolean)
   

if create_cowrie_commands_data_table:
    print('Creating table:', cowrie_commands_data_table_name)
    class CowrieCommandsData(Base):
        __tablename__ = cowrie_commands_data_table_name

        id = Column(Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
        sensor = Column(String(50))
        node_name = Column(String(30))
        session = Column(String(15))
        timestamp = Column(DateTime)
        command = Column(String(1000))
        commands_counter = Column(Integer)
        curl = Column(Boolean)
        wget = Column(Boolean)
        wget_curl_url = Column(String(200))
        commands_order = Column(Integer)
        delay_in_s = Column(Float)
        command_len = Column(Integer)
        ftp = Column(Boolean)
                 

print('Creating table:', TABLE_NAME)
class CowrieData(Base):
    __tablename__ = TABLE_NAME

    if insert_in_table_session:
        session = Column(String(15), primary_key=True)
    if insert_in_table_event_counter:    
        event_counter = Column(Integer)
    if insert_in_table_node_name:
        node_name = Column(String(30))
    if insert_in_table_src_ip:
        src_ip = Column(String(16))
    if insert_in_table_protocol:
        protocol = Column(String(10))
    if insert_in_table_dst_port:
        dst_port = Column(Integer)
    if insert_in_table_dst_ip:
        dst_ip = Column(String(16))  
    if insert_in_table_src_port:
        src_port = Column(Integer)
    if insert_in_table_sensor:
        sensor = Column(String(50))
    if insert_in_table_connect_timestamp:
        connect_timestamp = Column(DateTime)
    if insert_in_table_country_name:
        country_name = Column(String(30))
    if insert_in_table_location_lon:
        location_lon = Column(Float)
    if insert_in_table_location_lat:
        location_lat = Column(Float)
    if insert_in_table_closed_timestamp:    
        closed_timestamp = Column(DateTime)
    if insert_in_table_duration:    
        duration = Column(Float)
    if insert_in_table_arch:
        arch = Column(String(30))
    if insert_in_table_file_downloaded:
        file_downloaded = Column(Boolean) 
    if insert_in_table_per_event_statistic:
        sess_con = Column(Integer)
        sess_par = Column(Integer)
        file_dwn = Column(Integer)
        fil_dw_f = Column(Integer)
        sess_cls = Column(Integer)
        clt_vers = Column(Integer)
        clt_kex = Column(Integer)
        clt_var = Column(Integer)
        comm_suc = Column(Integer)
        comm_fld = Column(Integer)
        comm_inp = Column(Integer)
        d_tcp_re = Column(Integer)
        logn_suc = Column(Integer)
        d_tcp_da = Column(Integer)
        log_cls = Column(Integer)
        logn_fld = Column(Integer)
    if insert_in_table_login_statistics:
        login_tried = Column(Boolean)
        login_success = Column(Boolean)
        login_count_failed = Column(Integer)
        login_usr_success = Column(String(100))
        login_pass_success = Column(String(100))
    if insert_in_table_command_statistics:
        command_tried = Column(Boolean)
        command_counter = Column(Integer)
        command_avrage_delay = Column(Float)
        command_std_delay = Column(Float)  
        command_empty_counter = Column(Integer)
        command_timedelta_login = Column(Float)  

Base.metadata.create_all(engine)
