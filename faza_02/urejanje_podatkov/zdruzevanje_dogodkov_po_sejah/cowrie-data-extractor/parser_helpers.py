from outputs import SQLDatabaseOutput

import pandas as pd
import configparser
import copy
import datetime
import logging

config = configparser.ConfigParser()
config.read('./cowrie-data-extractor.conf')

database_output = SQLDatabaseOutput()

def parse_time_intervals(start_time, end_time, interval):
    datetime_object_start = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
    datetime_object_end = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')
    difference = datetime_object_end - datetime_object_start
    delta = int(difference / datetime.timedelta(minutes=interval))

    times = []
    temp_start_time = datetime_object_start

    for _ in range(delta):
        end_time = temp_start_time + datetime.timedelta(minutes=interval)  
        times.append((temp_start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'), end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')))
        temp_start_time = end_time

    return times   

def get_round_times(dt=None, date_delta=datetime.timedelta(minutes=10), to='down', interval=10):
    """
    Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
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

    time_start = time - 2*datetime.timedelta(minutes=interval)
    time_start = time_start.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    time_end = time - datetime.timedelta(minutes=interval)
    time_end = time_end.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    return (time_start, time_end)


class SessionParser:
    def __init__(self, elastic_search_result, max_query_size):
        self.elastic_search_result = elastic_search_result
        self._session_result_list = list()
        self._unique_session_result_list = list()
        self._session_counter = 0
        self._total_hits = int(self.elastic_search_result['hits']['total'])
        self.max_query_size = max_query_size
        self._get_all_close_sesion_id()

    def _check_total_hits(self):
        if self._total_hits >= self.max_query_size:
            return False
        else:
            return True

    def _get_all_close_sesion_id(self):
        '''This function parse the elasticsearch object to return sessions id for all events in a list.'''
        if self._check_total_hits():
            for count, hit in enumerate(self.elastic_search_result['hits']['hits']):
                self._session_result_list.append(hit['_source']['session'])

            self._session_counter = count
            return  self._session_result_list

        else:
            logging.error('Total number of sessions: ' + str(self._total_hits))
            logging.error('MAX_QUERY_RESULT_SIZE:' +  str(self.max_query_size))
            logging.critical('Number of sessions exceed the MAX_QUERY_RESULT_SIZE')
            raise ValueError('ERROR: Number of sessions exceed the MAX_QUERY_RESULT_SIZE')


    def _get_unique_sessions_ids(self):
        self._unique_session_result_list = list(set(self._session_result_list))
        return self._unique_session_result_list

    def get_unique_sessions_ids_count(self):
        return len(self._get_unique_sessions_ids())

    def save_unique_sessions(self, file_name='./data/unique_sessions.txt'):
        '''Save unique session to file to be analized, later we can change to SQLlite or simmiilar'''
        with open(file_name, 'w') as f: #TODO spremeni v appned ko bo končano brisnaje
            for item in self._get_unique_sessions_ids():
                f.write("%s\n" % item)


class DataParser:
    '''Class for parsing raw data form Elasticsearch. 
    Functions:
    - get_session_data(): TODO.....

    '''
    def __init__(self, elastic_query_data_raw, session_id):
        self.elastic_query_data_raw = elastic_query_data_raw
        self.par_session = session_id
        self.par_num_of_events = self.elastic_query_data_raw['hits']['total']

        self.par_number_of_cowrie_session_connect = 0
        self.par_number_of_cowrie_session_params = 0
        self.par_number_of_cowrie_session_file_download = 0
        self.par_number_of_cowrie_session_file_download_failed = 0
        self.par_number_of_cowrie_session_closed = 0
        self.par_number_of_cowrie_client_version = 0
        self.par_number_of_cowrie_client_kex = 0
        self.par_number_of_cowrie_client_var = 0
        self.par_number_of_cowrie_command_success = 0
        self.par_number_of_cowrie_command_failed = 0
        self.par_number_of_cowrie_command_input = 0
        self.par_number_of_cowrie_direct_tcpip_request = 0
        self.par_number_of_cowrie_login_success = 0
        self.par_number_of_cowrie_direct_tcpip_data = 0
        self.par_number_of_cowrie_log_closed = 0
        self.par_number_of_cowrie_login_failed = 0

        
        # Parsed data - cowrie_session_connect
        self.par_node_name = ''
        self.par_src_ip = ''
        self.par_protocol = ''
        self.par_dst_ip = ''
        self.par_dst_port = 0
        self.par_src_port = 0
        self.par_sensor = ''
        self.par_connect_timestamp = ''
        self.par_country_name = ''
        self.par_location_lon = 0.0
        self.par_location_lat = 0.0

        # Parsed data - cowrie_session_closed
        self.par_closed_timestamp = ''
        self.par_duration = 0.0

        # Parsed data - cowrie_session_params
        self.par_arch = None

        # Parsed data - cowrie_session_file_download & cowrie_session_file_download_failed
        self.par_file_download = False

        # Parsed data - cowrie_client_version
        # self.par_client_version = ''

        # Parsed data - cowrie_login_success & cowrie_login_failed
        self.par_login_tried = False
        self.par_login_success = False
        self.par_login_usr_success = None
        self.par_login_pass_success = None
        self.par_login_usr_failed = []
        self.par_login_pass_failed = []
        self.par_login_success_timestamp = None

        # Parsed data - cowrie.command.success & cowrie.command.failed & cowrie.command.input
        self.par_command_input = []
        self.par_command_tried = False
        self.par_command_avrage_delay = None
        self.par_command_std_delay = None
        self.par_number_of_empty_commands = 0
        self.par_first_command_timestamp = None
        self.par_timedelta_login_first_command = None
        

        ## CONFIG FOR ADDING TABLES
        self.create_cowrie_login_data_table = config.getboolean('TABLES_CREATE', 'create_cowrie_login_data_table')
        self.create_cowrie_commands_data_table = config.getboolean('TABLES_CREATE', 'create_cowrie_commands_data_table')
        
        ## CONFIG FOR ADDING ROWS IN THE TABLE
        self.insert_in_table_node_name = config.getboolean('TABLES_COLUMNS', 'node_name') 
        self.insert_in_table_session = config.getboolean('TABLES_COLUMNS', 'session') 
        self.insert_in_table_event_counter = config.getboolean('TABLES_COLUMNS', 'event_counter')
        self.insert_in_table_src_ip = config.getboolean('TABLES_COLUMNS', 'src_ip')
        self.insert_in_table_protocol = config.getboolean('TABLES_COLUMNS', 'protocol')
        self.insert_in_table_dst_port = config.getboolean('TABLES_COLUMNS', 'dst_port')
        self.insert_in_table_dst_ip = config.getboolean('TABLES_COLUMNS', 'dst_ip')
        self.insert_in_table_src_port = config.getboolean('TABLES_COLUMNS', 'src_port')
        self.insert_in_table_sensor = config.getboolean('TABLES_COLUMNS', 'sensor')
        self.insert_in_table_connect_timestamp = config.getboolean('TABLES_COLUMNS', 'connect_timestamp')
        self.insert_in_table_country_name = config.getboolean('TABLES_COLUMNS', 'country_name')
        self.insert_in_table_location_lon = config.getboolean('TABLES_COLUMNS', 'location_lon')
        self.insert_in_table_location_lat = config.getboolean('TABLES_COLUMNS', 'location_lat')
        self.insert_in_table_closed_timestamp = config.getboolean('TABLES_COLUMNS', 'closed_timestamp')
        self.insert_in_table_duration = config.getboolean('TABLES_COLUMNS', 'duration')
        self.insert_in_table_arch = config.getboolean('TABLES_COLUMNS', 'arch')
        self.insert_in_table_file_downloaded = config.getboolean('TABLES_COLUMNS', 'file_downloaded')
        self.insert_in_table_per_event_statistic = config.getboolean('TABLES_COLUMNS', 'per_event_statistic')
        self.insert_in_table_login_statistics = config.getboolean('TABLES_COLUMNS', 'login_statistics')
        self.insert_in_table_command_statistics = config.getboolean('TABLES_COLUMNS', 'command_statistics')



    def get_session_data(self):
        '''
        This function ... #TODO
        '''
    
        # Loop over all events in session
        for event in self.elastic_query_data_raw['hits']['hits']:

            # Check for cowrie.session.connect
            if event['_source']['eventid'] == 'cowrie.session.connect':
                self.par_number_of_cowrie_session_connect += 1
                self._parse_cowrie_session_connect(event)

            if event['_source']['eventid'] == 'cowrie.session.params':
                self.par_number_of_cowrie_session_params += 1
                self._parse_cowrie_session_params(event)

            if event['_source']['eventid'] == 'cowrie.session.file_download':
                self.par_number_of_cowrie_session_file_download += 1
                self._parse_cowrie_session_file_download(event)    

            if event['_source']['eventid'] == 'cowrie.session.file_download.failed':
                self.par_number_of_cowrie_session_file_download_failed += 1
                self._parse_cowrie_session_file_download_failed(event)    

            if event['_source']['eventid'] == 'cowrie.client.version':
                self.par_number_of_cowrie_client_version += 1
                
            if event['_source']['eventid'] == 'cowrie.client.kex':
                self.par_number_of_cowrie_client_kex += 1

            if event['_source']['eventid'] == 'cowrie.login.success': 
                self.par_number_of_cowrie_login_success += 1
                self._parse_cowrie_session_login(event)

            if event['_source']['eventid'] == 'cowrie.client.var': 
                self.par_number_of_cowrie_client_var += 1

            if event['_source']['eventid'] == 'cowrie.command.success': 
                self.par_number_of_cowrie_command_success += 1 
                # nothing to parse in this event
            
            if event['_source']['eventid'] == 'cowrie.command.failed': 
                self.par_number_of_cowrie_command_failed += 1
                # nothing to parse in this event

            if event['_source']['eventid'] == 'cowrie.command.input': 
                self.par_number_of_cowrie_command_input += 1
                self._parse_cowrie_command_input(event)

            if event['_source']['eventid'] == 'cowrie.direct-tcpip.data': 
                self.par_number_of_cowrie_direct_tcpip_data += 1 

            if event['_source']['eventid'] == 'cowrie.log.closed': 
                self.par_number_of_cowrie_log_closed += 1

            if event['_source']['eventid'] == 'cowrie.login.failed': 
                self.par_number_of_cowrie_login_failed += 1
                self._parse_cowrie_session_login(event)

            if event['_source']['eventid'] == 'cowrie.direct-tcpip.request': 
                self.par_number_of_cowrie_direct_tcpip_request += 1

            if event['_source']['eventid'] == 'cowrie.session.closed': 
                 self.par_number_of_cowrie_session_closed += 1
                 self._parse_cowrie_session_closed(event)

        

        # LOGIN DATA TABLE
        if self.create_cowrie_login_data_table:
            if (self.par_number_of_cowrie_login_success + self.par_number_of_cowrie_login_failed) == 0:
                pass
            else:
                login_events_per_session = []

                if self.par_number_of_cowrie_login_success > 0:
                    session_login_data_dict = dict()
                    session_login_data_dict['session'] = self.par_session
                    session_login_data_dict['sensor'] = self.par_sensor
                    session_login_data_dict['node_name'] = self.par_node_name
                    session_login_data_dict['username'] = self.par_login_usr_success
                    if len(session_login_data_dict['username']) > 99:
                        session_login_data_dict['username'] = 'USR_TOO_LONG'

                    session_login_data_dict['password'] = self.par_login_pass_success
                    if len(session_login_data_dict['password']) > 99:
                        session_login_data_dict['password'] = 'PASS_TOO_LONG'

                    session_login_data_dict['login_tries'] = self.par_number_of_cowrie_login_success + self.par_number_of_cowrie_login_failed
                    session_login_data_dict['success'] = True
                    
                    login_events_per_session.append(copy.deepcopy(session_login_data_dict))

                if self.par_number_of_cowrie_login_failed > 0:
                    session_login_data_dict = dict()
                    for username, password in zip(self.par_login_usr_failed, self.par_login_pass_failed):
                        session_login_data_dict['session'] = self.par_session
                        session_login_data_dict['node_name'] = self.par_node_name
                        session_login_data_dict['sensor'] = self.par_sensor
                        session_login_data_dict['username'] = username
                        if len(session_login_data_dict['username']) > 99:
                            session_login_data_dict['username'] = 'USR_TOO_LONG'

                        session_login_data_dict['password'] = password
                        if len(session_login_data_dict['password']) > 99:
                            session_login_data_dict['password'] = 'PASS_TOO_LONG'

                        session_login_data_dict['login_tries'] = self.par_number_of_cowrie_login_success + self.par_number_of_cowrie_login_failed
                        session_login_data_dict['success'] = False
                        
                        login_events_per_session.append(copy.deepcopy(session_login_data_dict))

                login_data = pd.DataFrame(login_events_per_session)
                database_output.add_data_to_table_login_data(login_data)

        # COMMANDS DATA TABLE
        if self.par_number_of_cowrie_command_input == 0 or len(self.par_command_input) == 0:
            pass 
        else:
            commands_event_per_session = []
            self.par_command_tried = True

            for command_timestamp in self.par_command_input:
                session_command_data_dict = dict()
                session_command_data_dict['session'] = self.par_session
                session_command_data_dict['sensor'] = self.par_sensor
                session_command_data_dict['node_name'] = self.par_node_name
                session_command_data_dict['timestamp'] = command_timestamp[0]
                session_command_data_dict['command'] = command_timestamp[1]
                session_command_data_dict['commands_counter'] = self.par_number_of_cowrie_command_input
                session_command_data_dict['wget'] = False
                session_command_data_dict['curl'] = False
                session_command_data_dict['wget_curl_url'] = None
                session_command_data_dict['ftp'] = None
                session_command_data_dict['command_len'] = command_timestamp[2]

                # check for ftp
                if 'ftp' in session_command_data_dict['command']:
                    session_command_data_dict['ftp'] = True

                # check for wget
                if 'wget' in session_command_data_dict['command']:
                    session_command_data_dict['wget'] = True
                    if 'http' in session_command_data_dict['command']:
                        f = session_command_data_dict['command'].find('http')
                        session_command_data_dict['wget_curl_url'] = session_command_data_dict['command'][f:].split(' ')[0].strip(';')

                # check for curl
                if 'curl' in session_command_data_dict['command']:
                    session_command_data_dict['curl'] = True  
                    if 'http' in session_command_data_dict['command']:
                        f = session_command_data_dict['command'].find('http')
                        session_command_data_dict['wget_curl_url'] = session_command_data_dict['command'][f:].split(' ')[0].strip(';')  

                # check for empty commands
                if session_command_data_dict['command'] == '':
                    continue

                
                commands_event_per_session.append(copy.deepcopy(session_command_data_dict))             
                
            
            command_data = pd.DataFrame(commands_event_per_session)
            command_data['timestamp'] = pd.to_datetime(command_data['timestamp'])
            command_data.sort_values(by=['timestamp'], inplace=True)
            command_data['commands_order'] = pd.Series(range(1,command_data.shape[0]+1))
            command_data['delay_in_s'] = (command_data['timestamp']-command_data['timestamp'].shift())
            command_data['delay_in_s'] = command_data['delay_in_s'].apply(lambda x: x.total_seconds())
            command_data.loc[0,'delay_in_s'] = 0
            self.par_first_command_timestamp = command_data[command_data['commands_order'] == 1]['timestamp'][0].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            

            
            self.par_command_avrage_delay = command_data['delay_in_s'].mean()
            self.par_command_std_delay = command_data['delay_in_s'].std()

            if self.create_cowrie_commands_data_table:     
                database_output.add_data_to_table_command_data(command_data)
        
        # Create output dict
        session_data_dict = dict()

        if self.insert_in_table_session:
            session_data_dict['session'] = self.par_session
        if self.insert_in_table_node_name:
            session_data_dict['node_name'] = self.par_node_name
        if self.insert_in_table_event_counter:
            session_data_dict['event_counter'] = self.par_num_of_events
        if self.insert_in_table_per_event_statistic:
            session_data_dict['sess_con'] = self.par_number_of_cowrie_session_connect
            session_data_dict['sess_par'] = self.par_number_of_cowrie_session_params
            session_data_dict['file_dwn'] = self.par_number_of_cowrie_session_file_download
            session_data_dict['fil_dw_f'] = self.par_number_of_cowrie_session_file_download_failed
            session_data_dict['sess_cls'] = self.par_number_of_cowrie_session_closed
            session_data_dict['clt_vers'] = self.par_number_of_cowrie_client_version
            session_data_dict['clt_kex'] = self.par_number_of_cowrie_client_kex
            session_data_dict['clt_var'] = self.par_number_of_cowrie_client_var
            session_data_dict['comm_suc'] = self.par_number_of_cowrie_command_success
            session_data_dict['comm_fld'] = self.par_number_of_cowrie_command_failed
            session_data_dict['comm_inp'] = self.par_number_of_cowrie_command_input
            session_data_dict['d_tcp_re'] = self.par_number_of_cowrie_direct_tcpip_request
            session_data_dict['logn_suc'] = self.par_number_of_cowrie_login_success
            session_data_dict['d_tcp_da'] = self.par_number_of_cowrie_direct_tcpip_data
            session_data_dict['log_cls'] = self.par_number_of_cowrie_log_closed
            session_data_dict['logn_fld'] = self.par_number_of_cowrie_login_failed
        if self.insert_in_table_src_ip:
            session_data_dict['src_ip'] = self.par_src_ip
        if self.insert_in_table_protocol:
            session_data_dict['protocol'] = self.par_protocol    
        if self.insert_in_table_dst_port:
            session_data_dict['dst_port'] = self.par_dst_port  
        if self.insert_in_table_dst_ip:
            session_data_dict['dst_ip'] = self.par_dst_ip
        if self.insert_in_table_src_port:
            session_data_dict['src_port'] = self.par_src_port
        if self.insert_in_table_sensor:
            session_data_dict['sensor'] = self.par_sensor
        if self.insert_in_table_connect_timestamp:
            session_data_dict['connect_timestamp'] = self.par_connect_timestamp
        if self.insert_in_table_country_name:
            session_data_dict['country_name'] = self.par_country_name
        if self.insert_in_table_location_lon:
            session_data_dict['location_lon'] = self.par_location_lon
        if self.insert_in_table_location_lat:
            session_data_dict['location_lat'] = self.par_location_lat
        if self.insert_in_table_closed_timestamp:
            session_data_dict['closed_timestamp'] = self.par_closed_timestamp 
        if self.insert_in_table_duration:
            session_data_dict['duration'] = self.par_duration    
        if self.insert_in_table_arch:
            session_data_dict['arch'] = self.par_arch
        if self.insert_in_table_file_downloaded:
            session_data_dict['file_downloaded'] = self.par_file_download
        if self.insert_in_table_login_statistics:
            session_data_dict['login_tried'] = self.par_login_tried
            session_data_dict['login_success'] = self.par_login_success
            session_data_dict['login_count_failed'] = self.par_number_of_cowrie_login_failed
            session_data_dict['login_usr_success'] = self.par_login_usr_success
            try:
                if len(session_data_dict['login_usr_success']) > 99:
                    session_login_data_dict['login_usr_success'] = 'USR_TOO_LONG'
            except TypeError:
                pass

            session_data_dict['login_pass_success'] = self.par_login_pass_success
            try:
                if len(session_data_dict['login_pass_success']) > 99:
                    session_login_data_dict['login_pass_success'] = 'PASS_TOO_LONG'
            except TypeError:
                pass        

        if self.insert_in_table_command_statistics:
            session_data_dict['command_tried'] = self.par_command_tried
            session_data_dict['command_counter'] = self.par_number_of_cowrie_command_input
            session_data_dict['command_avrage_delay'] = self.par_command_avrage_delay
            session_data_dict['command_std_delay'] = self.par_command_std_delay
            session_data_dict['command_empty_counter'] = self.par_number_of_empty_commands
            if self.par_login_success_timestamp and self.par_first_command_timestamp:
                par_login_success_timestamp_obj = datetime.datetime.strptime(self.par_login_success_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                par_first_command_timestamp_obj = datetime.datetime.strptime(self.par_first_command_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                self.par_timedelta_login_first_command = (par_first_command_timestamp_obj - par_login_success_timestamp_obj).total_seconds()
                session_data_dict['command_timedelta_login'] = self.par_timedelta_login_first_command

        return session_data_dict

    # PARSE FUNCTIONS
    def _parse_cowrie_session_connect(self, object):
        '''
        Parse the cowrie.session.connect object.
        Set the next values:
        -self.par_src_ip
        -self.par_protocol
        -self.par_dst_ip
        -self.par_dst_port
        -self.par_src_port
        -self.par_sensor
        -self.par_connect_timestamp
        -self.par_country_name
        -self.par_location_lon
        -self.par_location_lat

        '''
        object_data = object['_source']
        if object_data['eventid'] == 'cowrie.session.connect':

            # node_name
            try: 
                self.par_node_name = object_data['fields']['type']
            except KeyError:
                self.par_node_name = None
                logging.error('No node_name found for session: ' + str(self.par_session))

            # src_ip
            try: 
                self.par_src_ip = object_data['src_ip']
            except KeyError:
                self.par_src_ip = None
                logging.error('No src_ip found for session: ' + str(self.par_session))

            # dst_port
            try:
                self.par_dst_port = int(object_data['dst_port'])
            except KeyError:
                self.par_dst_port = None
                logging.error('No dst_port found for session: ' + str(self.par_session))

            # protocol
            try:
                self.par_protocol = object_data['protocol']
            except KeyError:
                if self.par_dst_port == 22 or 2222:
                    self.par_protocol = 'ssh'
                elif self.par_dst_port == 23 or 2223:
                    self.par_protocol = 'telnet'
                else:
                    self.par_protocol = None
                    logging.error('No protocol found for session: ' + str(self.par_session))

            # dst_ip
            try:
                self.par_dst_ip = object_data['dst_ip']
            except KeyError:
                self.par_dst_ip = None
                logging.error('No dst_ip found for session: ' + str(self.par_session))

            # src_port
            try:
                self.par_src_port = int(object_data['src_port'])
            except KeyError:
                self.par_src_port = None
                logging.error('No src_port found for session: ' + str(self.par_session))

            # sensor
            try:
                self.par_sensor = object_data['sensor']
            except KeyError:
                self.par_sensor = None
                logging.error('No sensor found for session: ' + str(self.par_session))
            
            # connect_timestamp
            try:
                self.par_connect_timestamp = object_data['timestamp']
            except KeyError:
                self.par_connect_timestamp = None
                logging.error('No connect_timestamp found for session: ' + str(self.par_session))


            # country_name, location_lon, location_lat
            if '_geoip_lookup_failure' in object_data['tags']:
                # TODO: v tem primeru daodaj funkcijo ki nardi geoip_lookup
                logging.info('_geoip_lookup_failure')
                self.par_country_name = None
                self.par_location_lon = None
                self.par_location_lat = None
            else:
                try: 
                    self.par_country_name = object_data['geoip']['country_name']
                except KeyError:
                    self.par_country_name = None
                    logging.error('No country_name found for session: ' + str(self.par_session))

                try:
                    self.par_location_lon = float(object_data['geoip']['longitude'])
                except KeyError:
                    self.par_location_lon = None
                    logging.error('No location_lon found for session: ' + str(self.par_session))

                try:
                    self.par_location_lat = float(object_data['geoip']['latitude'])
                except KeyError:
                    self.par_location_lat = None
                    logging.error('No location_lat found for session: ' + str(self.par_session))
                                
    def _parse_cowrie_session_closed(self, object):
        '''
        Parse the cowrie_session_closed object.
        Set the next values:
        - self.par_closed_timestamp
        - self.par_duration
        '''
        object_data = object['_source']
        if object_data['eventid'] == 'cowrie.session.closed':

            # closed_timestamp
            try: 
                self.par_closed_timestamp = object_data['timestamp']
            except KeyError:
                self.par_closed_timestamp = None
                logging.error('No closed_timestamp found for session: ' + str(self.par_session))

            # duration
            try: 
                self.par_duration = round(float(object_data['duration']), 6)
            except KeyError:
                self.par_duration = None
                logging.error('No duration found for session: ' + str(self.par_session))   

    def _parse_cowrie_session_params(self, object):
        '''
        Parse the cowrie_session_params object.
        Set the next values:
        - self.par_arch
        '''
        object_data = object['_source']
        if object_data['eventid'] == 'cowrie.session.params':

            # arch
            try:
                self.par_arch = object_data['arch']
            except KeyError:
                self.par_arch = None
                logging.error('No arch found for session: ' + str(self.par_session))

    def _parse_cowrie_session_file_download(self, object):
        '''
        Parse the cowrie_session_file_download object.
        Set the next values:
        - self.par_file_download
        '''
        object_data = object['_source']
        if object_data['eventid'] == 'cowrie.session.file_download':

            # file_download
            self.par_file_download = True
            

    def _parse_cowrie_session_file_download_failed(self, object):
        '''
        Parse the session_file_download_failed object.
        Set the next values:
        - self.par_file_download
        '''
        object_data = object['_source']
        if object_data['eventid'] == 'cowrie.session.file_download.failed':

            # file_download
            self.par_file_download = True


    def _parse_cowrie_session_login(self, object):
        '''
        Parse the cowrie_login_success & cowrie_login_failed object.
        Set the next values:
        - par_login_tried 
        - par_login_success 
        - par_login_usr_success
        - par_login_pass_success
        - par_login_usr_failed
        - par_login_pass_failed
        '''
        object_data = object['_source']

        # login_tried 
        self.par_login_tried = True 

        if object_data['eventid'] == 'cowrie.login.success':
            self.par_login_success = True
            self.par_login_success_timestamp = object_data['timestamp']

            # login_usr_success
            try:
                self.par_login_usr_success = object_data['username']
            except KeyError:
                self.par_login_usr_success = None
                logging.error('No login_usr_success found for session: ' + str(self.par_session))

            # login_pass_success
            try:
                self.par_login_pass_success = object_data['password']
            except KeyError:
                self.par_login_pass_success = None
                logging.error('No login_pass_success found for session: ' + str(self.par_session))  


        if object_data['eventid'] == 'cowrie.login.failed':
            # login_usr_failed
            try: 
                self.par_login_usr_failed.append(object_data['username'])
            except KeyError:
                self.par_login_usr_failed = None
                logging.error('No login_usr_failed found for session: ' + str(self.par_session))     

            # login_pass_failed
            try: 
                self.par_login_pass_failed.append(object_data['password'])
            except KeyError:
                self.par_login_pass_failed = None
                logging.error('No login_pass_failed found for session: ' + str(self.par_session))         

    def _parse_cowrie_command_input(self, object):
        '''
        Parse the cowrie_command_input object.
        Set the next values:
        - par_command_failed
        '''

        object_data = object['_source']
        _command_len = 0

        if object_data['eventid'] == 'cowrie.command.input':
           
            # message - command input
            try:
                command = object_data['message'].split('CMD:')[-1].strip()
            except KeyError:
                command = None
                logging.error('No command_input found for session: ' + str(self.par_session))
            
            # command_timestamp
            try:
                time = object_data['timestamp']
            except KeyError:
                time = None
                logging.error('No command_timestamp found for session: ' + str(self.par_session))    

            if command == '' or command == ' ':
                self.par_number_of_empty_commands += 1
            elif len(command) > 1000:
                _command_len = len(command)
                command = 'Command too long: check session ' + str(self.par_session) + ' in Kibana for full command.'
                self.par_command_input.append((time, command, _command_len))
                logging.error('Command too long for session: ' + str(self.par_session))
            else: 
                _command_len = len(command)   
                self.par_command_input.append((time, command, _command_len))

            
