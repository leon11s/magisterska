import pandas as pd

from sqlalchemy import create_engine, Table
from sqlalchemy.types import Integer, String

from config_reader import (dialect, dbname, user, password, host, UNIQUE_SCRIPTS_TABLE_NAME, 
                            ALL_SCRIPTS_COLUMN_LEN, INPUT_TABLE_NAME,
                            GENERAL_TABLE_NAME, start_time, end_time)


def parse_database_connection_url(dialect, dbname, host, user, password):
    if dialect == 'sqlite':
        url = dialect + ':///' + dbname
    else:
        url = dialect + '://' + user + ':' + password + '@' + host + '/' + dbname

    return url


class SQLDatabaseInput():
    def __init__(self):
        url = parse_database_connection_url(dialect, dbname, host, user, password)
        print('SQLDatabaseInput: Connecting to:', url)
        self.engine = create_engine(url, echo=False)

    def get_session_ids(self, start_time_, end_time_, table_name=INPUT_TABLE_NAME):
        sessions = []

        query = 'SELECT session FROM ' + table_name + ' where timestamp > "' + start_time_ + '" and timestamp < "' + end_time_ + '";'
        with self.engine.connect() as con:
            sessions_row = con.execute(query)

        for session in sessions_row:
            sessions.append(session[0])

        sessions = list(set(sessions))    
        return sessions

    def get_command_data(self, session, table_name=INPUT_TABLE_NAME):
        results_clean = []
       
        query = 'SELECT session, commands_counter, command FROM ' + table_name + ' where session = "' + session + '";'
        
        with self.engine.connect() as con:
            results = con.execute(query)

        for result in results:
            results_clean.append(result)

        return results_clean

    def get_src_ip_from_session(self, session, table_name=GENERAL_TABLE_NAME):
        results_clean = []
        
        query = 'SELECT src_ip FROM ' + table_name + ' where session = "' + session + '"' 'LIMIT 1;'  

        with self.engine.connect() as con:
            results = con.execute(query)

        for result in results:
            results_clean.append(result)
        
        if not results_clean:
            return None

        return results_clean[0][0]

    def get_all_scripts_list(self, table_name=UNIQUE_SCRIPTS_TABLE_NAME):
        results_clean = []

        query = 'SELECT id, commands_string, repetitions_count FROM ' + table_name+ ';'

        with self.engine.connect() as con:
            results = con.execute(query)

        for result in results:
            results_clean.append(result) 

        return results_clean

class SQLDatabaseOutput():
    def __init__(self):
        url = parse_database_connection_url(dialect, dbname, host, user, password)
        print('SQLDatabaseOutput: Connecting to:', url)
        self.engine = create_engine(url, echo=False)

    def is_all_script_table_empty(self, table_name=UNIQUE_SCRIPTS_TABLE_NAME):
        query = 'SELECT * FROM ' + table_name + ' LIMIT 1;'

        with self.engine.connect() as con:
            results = con.execute(query)

        rows_amount = 0
        for row in results:
            rows_amount += 1

        if not rows_amount:
            return True
        else:
            return False
        
    def insert_new_script_to_all_scripts_table(self, data, table_name=UNIQUE_SCRIPTS_TABLE_NAME):
        data = [[data, 1]]
        data_df = pd.DataFrame(data, columns = ['commands_string', 'repetitions_count']) 

        type_dict = {}
        type_dict['commands_string'] = String(ALL_SCRIPTS_COLUMN_LEN)
        type_dict['repetitions_count'] = Integer() 

        data_df.to_sql(table_name, con=self.engine, if_exists='append', index=False, dtype=type_dict)

        query = 'SELECT id FROM ' + UNIQUE_SCRIPTS_TABLE_NAME + ' ORDER BY ID DESC LIMIT 1;'

        with self.engine.connect() as con:
            results = con.execute(query)

        return results.fetchall()[0][0]

    def add_one_to_counter(self, id_, table_name=UNIQUE_SCRIPTS_TABLE_NAME):
        query = 'UPDATE ' + table_name + ' SET repetitions_count = repetitions_count + 1 WHERE id = ' + str(id_) + ';'

        with self.engine.connect() as con:
            con.execute(query)


    def insert_analyzed_data(self, data, table_name=GENERAL_TABLE_NAME):
        pass

