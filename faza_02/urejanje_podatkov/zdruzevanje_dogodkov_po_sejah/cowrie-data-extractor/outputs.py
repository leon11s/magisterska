from sqlalchemy import create_engine
from sqlalchemy.types import Integer, String, DateTime, Float, Boolean

import pandas as pd
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
cowrie_commands_data_table_name = str(config['TABLES_CREATE']['cowrie_commands_data_table_name'])



class SQLDatabaseOutput():
    def __init__(self):
        if dialect == 'sqlite':
            url = dialect + ':///' + dbname
        else:
            url = dialect + '://' + user + ':' + password + '@' + host + '/' + dbname

        print('Connecting to:', url)
        self.engine = create_engine(url, echo=False)

    def add_data_to_table_main(self, data, table_name=TABLE_NAME):

        type_dict = {}

        if insert_in_table_session:
            type_dict['session'] = String(15)
       
        if insert_in_table_node_name:
            type_dict['node_name'] = String(30)
    
        if insert_in_table_event_counter:
            type_dict['event_counter'] = Integer()
        
        if insert_in_table_src_ip:
            type_dict['src_ip'] = String(16)
        
        if insert_in_table_protocol:
            type_dict['protocol'] = String(10)  
        
        if insert_in_table_dst_port:
            type_dict['dst_port'] = Integer() 
        
        if insert_in_table_dst_ip:
            type_dict['dst_ip'] = String(16)
       
        if insert_in_table_src_port:
            type_dict['src_port'] = Integer()
      
        if insert_in_table_sensor:
            type_dict['sensor'] = String(50)
        
        if insert_in_table_connect_timestamp:
            type_dict['connect_timestamp'] = DateTime()
            data['connect_timestamp'] =  pd.to_datetime(data['connect_timestamp'])
       
        if insert_in_table_country_name:
            type_dict['country_name'] = String(30)
        
        if insert_in_table_location_lon:
            type_dict['location_lon'] = Float()
        
        if insert_in_table_location_lat:
            type_dict['location_lat'] = Float()
        
        if insert_in_table_closed_timestamp:
            type_dict['closed_timestamp'] = DateTime()
            data['closed_timestamp'] =  pd.to_datetime(data['closed_timestamp'])
        
        if insert_in_table_duration:
            type_dict['duration'] = Float()    
       
        if insert_in_table_arch:
            type_dict['arch'] = String(30)

        if insert_in_table_file_downloaded:
            type_dict['file_downloaded'] = Boolean()
        
        
        if insert_in_table_per_event_statistic:
            type_dict['sess_con'] = Integer()
            type_dict['sess_par'] = Integer()
            type_dict['file_dwn'] = Integer()
            type_dict['fil_dw_f'] = Integer()
            type_dict['sess_cls'] = Integer()
            type_dict['clt_vers'] = Integer()
            type_dict['clt_kex'] = Integer()
            type_dict['clt_var'] = Integer()
            type_dict['comm_suc'] = Integer()
            type_dict['comm_fld'] = Integer()
            type_dict['comm_inp'] = Integer()
            type_dict['d_tcp_re'] = Integer()
            type_dict['logn_suc'] = Integer()
            type_dict['d_tcp_da'] = Integer()
            type_dict['log_cls'] = Integer()
            type_dict['logn_fld'] = Integer()

        if insert_in_table_login_statistics:
            type_dict['login_tried'] = Boolean()
            type_dict['login_success'] = Boolean()
            type_dict['login_count_failed'] = Integer()
            type_dict['login_usr_success'] = String(100)
            type_dict['login_pass_success'] = String(100)    

        if insert_in_table_command_statistics:
            type_dict['command_tried'] = Boolean()
            type_dict['command_counter'] = Integer()
            type_dict['command_avrage_delay'] = Float()    
            type_dict['command_std_delay'] = Float() 
            type_dict['command_empty_counter'] = Integer()
            type_dict['command_timedelta_login'] = Float()
      
        data.to_sql(table_name, con=self.engine, if_exists='append', index_label='session', dtype=type_dict)

    def add_data_to_table_login_data(self, data, table_name=cowrie_login_data_table_name):
        
        type_dict = {}

        type_dict['session'] = String(15)
        type_dict['sensor'] = String(50)
        type_dict['node_name'] = String(30)
        type_dict['username'] = String(100) 
        type_dict['password'] = String(100)
        type_dict['login_tries'] = Integer()   
        type_dict['success'] = Boolean()

        data.to_sql(table_name, con=self.engine, if_exists='append', index=False, dtype=type_dict)


    def add_data_to_table_command_data(self, data, table_name=cowrie_commands_data_table_name):
        
        type_dict = {}
        
        type_dict['sensor'] = String(50)
        type_dict['node_name'] = String(30)
        type_dict['session'] = String(15)
        type_dict['timestamp'] =DateTime()
        type_dict['command'] = String(1000)
        type_dict['commands_counter'] = Integer()
        type_dict['curl'] = Boolean()
        type_dict['wget'] = Boolean()
        type_dict['wget_curl_url'] = String(200)
        type_dict['commands_order'] = Integer()
        type_dict['delay_in_s'] = Float()
        type_dict['command_len'] = Integer()
        type_dict['ftp'] = Boolean()

 
        data.to_sql(table_name, con=self.engine, if_exists='append', index=False, dtype=type_dict)   



class ElasticsearchOutput():
    pass
    # TODO implementiraj dodajanje v ES

