import pandas as pd

from sqlalchemy.types import Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, create_engine

from database import parse_database_connection_url
from config_reader import FINAL_COMMAND_TABLE, GENERAL_TABLE_NAME, INPUT_TABLE_NAME, DEBUG, dialect, dbname, user, password, host

Base = declarative_base()

class TableDataField():
    def __init__(self, name, data, dtype, isnull):
        self.name = name
        self.data = data
        self.dtype = dtype
        self.isnull = isnull


class FinalCommandTable(Base):
    __tablename__ = FINAL_COMMAND_TABLE
    session = Column(String(15), primary_key=True, nullable=False, unique=True)
    src_ip = Column(String(16))
    command_id = Column(Integer())

    node_name = Column(String(30))
    protocol = Column(String(10))
    sensor = Column(String(50))
    timestamp = Column(DateTime())
    country_name = Column(String(30))
    session_duration = Column(Float())
    login_usr_success = Column(String(100))
    login_pass_success = Column(String(100))
    command_avrage_delay = Column(Float())
    commands_counter = Column(Integer())
    command_std_delay = Column(Float())
    command_empty_counter = Column(Integer())
    command_timedelta_login = Column(Float())

    curl = Column(Boolean())
    wget = Column(Boolean())
    ftp = Column(Boolean())
    command_len = Column(Integer())
    wget_curl_url = Column(String(200))

    is_human = Column(Integer())

class InsertFinalCommandTable():
    def __init__(self):
        # We check if final_command_table already exists
        self.url = parse_database_connection_url(dialect, dbname, host, user, password)
        self.engine = create_engine(self.url, echo=False)
        self.final_command_table_exists = self._checkTableExists(FINAL_COMMAND_TABLE)

        # If table doesn't exists, we create the table
        if not self.final_command_table_exists:
            if DEBUG: print('--> Creating table:', FINAL_COMMAND_TABLE)
            Base.metadata.create_all(self.engine)
            if DEBUG: print('Table successfully creted.')

    def insert_to_table(self, session, src_ip, command_id):
        self.tdf_session = self._get_session(session)
        self.tdf_src_ip = self._get_src_ip(src_ip)
        self.tdf_command_id = self._get_command_id(command_id)
        
        # Get data from general table 
        general_table_data = self._general_table_data(session, GENERAL_TABLE_NAME)

        self.tdf_node_name = self._get_node_name(general_table_data[0])
        self.tdf_protocol = self._get_protocol(general_table_data[1])
        self.tdf_sensor = self._get_sensor(general_table_data[2])
        self.tdf_timestamp = self._get_timestamp(general_table_data[3])
        self.tdf_country_name = self._get_country_name(general_table_data[4])
        self.tdf_session_duration = self._get_session_duration(general_table_data[5])
        self.tdf_login_usr_success = self._get_login_usr_success(general_table_data[6])
        self.tdf_login_pass_success = self._get_login_pass_success(general_table_data[7])
        self.tdf_command_avrage_delay = self._get_command_avrage_delay(general_table_data[8])
        self.tdf_command_counter = self._get_commands_counter(general_table_data[9])
        self.tdf_command_std_delay = self._get_command_std_delay(general_table_data[10])
        self.tdf_command_empty_counter = self._get_command_empty_counter(general_table_data[11])
        self.tdf_command_timedelta_login = self._get_command_timedelta_login(general_table_data[12])

        # Get data from command table
        command_table_data = self._command_table_data(session, INPUT_TABLE_NAME)

        self.tdf_curl = self._get_curl(command_table_data[0])
        self.tdf_wget = self._get_wget(command_table_data[1])
        self.tdf_ftp = self._get_ftp(command_table_data[2])
        self.tdf_command_len = self._get_command_len(command_table_data[3])
        self.tdf_wget_curl_url = self._get_wget_curl_url(command_table_data[4])

        self.tdf_is_human = self._get_is_human()

        # list with all objects to add into table
        dtf_object_list = [self.tdf_session, self.tdf_src_ip, self.tdf_command_id, self.tdf_node_name, 
                           self.tdf_protocol, self.tdf_sensor, self.tdf_timestamp, self.tdf_country_name, 
                           self.tdf_session_duration, self.tdf_login_usr_success, self.tdf_login_pass_success,
                           self.tdf_command_avrage_delay, self.tdf_command_counter, self.tdf_command_std_delay,
                           self.tdf_command_empty_counter, self.tdf_command_timedelta_login, self.tdf_curl,
                           self.tdf_wget, self.tdf_ftp, self.tdf_command_len, self.tdf_wget_curl_url, self.tdf_is_human]

        self.data_df = pd.DataFrame([''], columns = ['session']) 
        self.data_df_type_dict = {}
        
        # Create object with all data for insert in table
        self._create_insert_object(dtf_object_list)
        self._db_insert_row(FINAL_COMMAND_TABLE)
        if DEBUG: print('--> inser_final_table.py: Session added to table:', self.tdf_session.data)
        

    def _checkTableExists(self, table_name):
        query = 'SELECT * FROM information_schema.tables WHERE table_name = "' + table_name + '";'
        with self.engine.connect() as con:
            results = con.execute(query)

        result = results.fetchone()    
        if result == None:
            return False
        elif result[2] == FINAL_COMMAND_TABLE:
            return True
        
    def _create_insert_object(self, dtf_object_list):
        for dtf_object in dtf_object_list:
            self.data_df[dtf_object.name] = dtf_object.data
            self.data_df_type_dict[dtf_object.name] = dtf_object.dtype

    def _db_insert_row(self,table_name):
        self.data_df.to_sql(table_name, con=self.engine, if_exists='append', index=False, dtype=self.data_df_type_dict)

    def _general_table_data(self, session, table_name):
        query = 'SELECT node_name, protocol, sensor, connect_timestamp, country_name, duration, login_usr_success, \
                login_pass_success, command_avrage_delay, command_counter, command_std_delay, command_empty_counter, command_timedelta_login FROM ' \
                 + table_name + ' where session = "' + session + '";'
        
        with self.engine.connect() as con:
            results = con.execute(query)

        results_clean = results.fetchone()

        if results_clean == None:
            results_clean = [None for x in range(13)]

        return results_clean
    
    def _command_table_data(self, session, table_name):
        query = 'SELECT curl, wget, ftp, command_len, wget_curl_url FROM ' \
                 + table_name + ' where session = "' + session + '";'
        
        with self.engine.connect() as con:
            results = con.execute(query)

        results_clean = results.fetchone()

        if results_clean == None:
            results_clean = [None for x in range(5)]

        return results_clean

    # Parse functions
    def _get_session(self, session):
        '''
        ID of the attacker session (unique): str(15)
        '''
        isnull = False
        if (session == '') or (session == None):
            session = None
            isnull = True
        return TableDataField('session', session, String(15), isnull)

    def _get_src_ip(self, src_ip):
        '''
        Source IP of the attacker: str(16)
        '''
        isnull = False
        if (src_ip == '') or (src_ip == None):
            src_ip = None
            isnull = True
        return TableDataField('src_ip', src_ip, String(16), isnull)


    def _get_command_id(self, command_id):
        '''
        The ID of the command in the ALL_SCRIPT_TABLE: Integer
        '''
        isnull = False
        if (command_id == '') or (command_id == None):
            command_id = None
            isnull = True
        return TableDataField('command_id', command_id, Integer(), isnull)

    def _get_sensor(self, sensor):
        '''
        The sensor name: str(50)
        '''
        isnull = False
        if (sensor == '') or (sensor == None):
            sensor = None
            isnull = True
        return TableDataField('sensor', sensor, String(50), isnull)

    def _get_node_name(self, node_name):
        '''
        The name of the node on K8S cluster: str(30)
        '''
        isnull = False
        if (node_name == '') or (node_name == None):
            node_name = None
            isnull = True
        return TableDataField('node_name', node_name,  String(30), isnull)

    def _get_timestamp(self, timestamp):
        '''
        Timestamp of the inserted command: DateTime
        '''
        isnull = False
        if (timestamp == '') or (timestamp == None):
            timestamp = None
            isnull = True
        return TableDataField('timestamp', timestamp,  DateTime(), isnull)   

    def _get_commands_counter(self, commands_counter):
        '''
        Number of all commands in a session: Integer
        '''
        isnull = False
        if (commands_counter == '') or (commands_counter == None):
            commands_counter = None
            isnull = True
        return TableDataField('commands_counter', commands_counter, Integer(), isnull)  

    def _get_curl(self, curl):
        '''
        True if curl used in session commands: Boolean
        '''
        isnull = False
        if (curl == '') or (curl == None):
            curl = None
            isnull = True
        return TableDataField('curl', curl, Boolean(), isnull)  

    def _get_wget(self, wget):
        '''
        True if wget used in session commands: Boolean
        '''
        isnull = False
        if (wget == '') or (wget == None):
            wget = None
            isnull = True
        return TableDataField('wget', wget, Boolean(), isnull)  

    def _get_ftp(self, ftp):
        '''
        True if ftp used in session commands: Boolean
        '''
        isnull = False
        if ftp == None:
            ftp = False

        if (ftp == ''):
            ftp = None
            isnull = True
        return TableDataField('ftp', ftp, Boolean(), isnull)           

    def _get_wget_curl_url(self, wget_curl_url):
        '''
        URL used in curl or wget: str(200)
        '''
        isnull = False
        if (wget_curl_url == '') or (wget_curl_url == None):
            wget_curl_url = None
            isnull = True
        return TableDataField('wget_curl_url', wget_curl_url,  String(200), isnull)     

    def _get_command_avrage_delay(self, command_avrage_delay):
        '''
        Avrage time between commands: Float
        '''
        isnull = False
        if (command_avrage_delay == '') or (command_avrage_delay == None):
            command_avrage_delay = None
            isnull = True
        return TableDataField('command_avrage_delay', command_avrage_delay, Float(), isnull) 

    def _get_command_std_delay(self, command_std_delay):
        '''
        STD between commands: Float
        '''
        isnull = False
        if (command_std_delay == '') or (command_std_delay == None):
            command_std_delay = None
            isnull = True
        return TableDataField('command_std_delay', command_std_delay, Float(), isnull)        

    def _get_command_len(self, command_len):
        '''
        Lenght of command string: Integer
        '''
        isnull = False
        if (command_len == '') or (command_len == None):
            command_len = None
            isnull = True
        return TableDataField('command_len', command_len, Integer(), isnull) 

    def _get_command_empty_counter(self, command_empty_counter):
        '''
        Number of empty line in a session: Integer
        '''
        isnull = False
        if (command_empty_counter == '') or (command_empty_counter == None):
            command_empty_counter = None
            isnull = True
        return TableDataField('command_empty_counter', command_empty_counter, Integer(), isnull) 

    def _get_command_timedelta_login(self, command_timedelta_login):
        '''
        Number of seconds between the login and the first command: Float
        '''
        isnull = False
        if (command_timedelta_login == '') or (command_timedelta_login == None):
            command_timedelta_login = None
            isnull = True
        return TableDataField('command_timedelta_login', command_timedelta_login, Float(), isnull)               

    def _get_login_usr_success(self, login_usr_success):
        '''
        Username of the attacker to login in the honeypot: str(100)
        '''
        isnull = False
        if (login_usr_success == '') or (login_usr_success == None):
            login_usr_success = None
            isnull = True
        return TableDataField('login_usr_success', login_usr_success, String(100), isnull)

    def _get_login_pass_success(self, login_pass_success):
        '''
        Password of the attacker to login in the honeypot: str(100)
        '''
        isnull = False
        if (login_pass_success == '') or (login_pass_success == None):
            login_pass_success = None
            isnull = True
        return TableDataField('login_pass_success', login_pass_success, String(100), isnull)

    def _get_country_name(self, country_name):
        '''
        The name of the src_ip country: str(30)
        '''
        isnull = False
        if (country_name == '') or (country_name == None):
            country_name = None
            isnull = True
        return TableDataField('country_name', country_name,  String(30), isnull) 

    def _get_protocol(self, protocol):
        '''
        The name of the protocol (ssh/telnet): str(10)
        '''
        isnull = False
        if (protocol == '') or (protocol == None):
            protocol = None
            isnull = True
        return TableDataField('protocol', protocol,  String(10), isnull)

    def _get_session_duration(self, session_duration):
        '''
        The duration of the session: Float
        '''
        isnull = False
        if (session_duration == '') or (session_duration == None):
            session_duration = None
            isnull = True
        return TableDataField('session_duration', session_duration, Float(), isnull)       

    def _get_is_human(self):
        '''
        If script is written by human: Integer
        Codes:
            - 0: False
            - 1: True
            - 2: Maybe
            - 3: Not checked
        '''
        isnull = False
        is_human = 3
        return TableDataField('is_human', is_human, Integer(), isnull)            
          


        

if __name__ == "__main__":
    import random
    import string
    import sys

    def randomString(stringLength=10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def drop_table(object):
        query = 'DROP TABLE ' + FINAL_COMMAND_TABLE + ';'
        with object.engine.connect() as con:
            con.execute(query)    
        print('TABLE DROPPED!')   

    if sys.argv[1] == 'drop':  
        table = InsertFinalCommandTable()
        drop_table(table)
    else:
        table = InsertFinalCommandTable()
        drop_table(table)

        table.insert_to_table(randomString() , None, None)
        print('-----')

        table.insert_to_table(randomString()  , '', 4)
        print('-----')

        table.insert_to_table('edb6d606ecbd'  , '25.89.855.74', 25)
        print('-----')

        table.insert_to_table('00008e1b45ed' , '212.185.45.74', 1)
        print('-----')