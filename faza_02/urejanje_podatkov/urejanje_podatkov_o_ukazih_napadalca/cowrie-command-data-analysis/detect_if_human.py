#!/usr/bin/env python3
import logging
import datetime

from sqlalchemy import create_engine
from config_reader import dialect, dbname, user, password, host, FINAL_COMMAND_TABLE

TEST = True
DEBUG = True

class DatabaseConnect():
    def __init__(self):
        self.url = self._create_url(dialect, dbname, host, user, password)
        self.engine = create_engine(self.url, echo=False)
        if DEBUG: logging.warning('Connected to database: ' + str(self.url))

    def _create_url(self, dialect, dbname, host, user, password):
        if dialect == 'sqlite':
            url = dialect + ':///' + dbname
        else:
            url = dialect + '://' + user + ':' + password + '@' + host + '/' + dbname
        return url

    def get_rows(self, table_name, columns='all', nrows='all'):
        # column parameter settings
        if columns == 'all':
            query = 'SELECT * FROM ' + table_name + ';'
        elif isinstance(columns, list):
            if len(columns) >= 1:
                column_names = ', '.join(columns)
                query = 'SELECT ' + column_names + ' FROM ' + table_name + ';'
            else:
                if DEBUG: logging.warning('get_rows: No columns names in list.')
                return []
        else: 
            if DEBUG: logging.warning('get_rows: columns parameter should be list or "all".')
            return []

        with self.engine.connect() as con:
            results = con.execute(query)    

        #nrows parameter setting
        results_clean = []

        if isinstance(nrows, int):
            if nrows == 1:
                results_clean.append(results.fetchone())
                return results_clean
            elif nrows > 1:
                results_clean = results.fetchmany(5)
                return results_clean   
            else:
                if DEBUG: logging.warning('get_rows: nrows parameter wrong.')
                return []
        elif nrows == 'all':
            results_clean = results.fetchall()
            return results_clean 
        else:
            if DEBUG: logging.warning('get_rows: nrows parameter wrong.')
            return []






def main():
    conn = DatabaseConnect()


def test():
    # set up logging
    try:
        logging.basicConfig(level=logging.WARNING, filename='output_data/detect_if_human.log', filemode='a')
    except FileNotFoundError:
        open('output_data/detect_if_human.log', 'w').close()
        logging.basicConfig(level=logging.WARNING, filename='output_data/detect_if_human.log', filemode='a')

    current_time = datetime.datetime.now()
    if DEBUG: logging.warning('detect_if_human started at: ' + str(current_time))

    conn = DatabaseConnect()
    sessions = conn.get_rows(FINAL_COMMAND_TABLE, columns=['session'], nrows='all')





    conn.get_rows(FINAL_COMMAND_TABLE, columns='all', nrows=5)
    print('-------------')
    conn.get_rows(FINAL_COMMAND_TABLE, columns=[], nrows=5)
    print('-------------')
    conn.get_rows(FINAL_COMMAND_TABLE, columns=12, nrows=5)
    print('-------------')
    conn.get_rows(FINAL_COMMAND_TABLE, columns=['node_name'], nrows=5)
    print('-------------')
    conn.get_rows(FINAL_COMMAND_TABLE, columns=['node_name', 'command_id', 'src_ip'], nrows=5)
    print('-------------')
    results = conn.get_rows(FINAL_COMMAND_TABLE, columns=['node_name', 'command_id', 'src_ip'], nrows=1)

    print('-------------')
    results = conn.get_rows(FINAL_COMMAND_TABLE, columns=['node_name', 'command_id', 'src_ip'], nrows=5)
   
    
    print('************')
    print(results)






if __name__ == "__main__":
    if TEST:
        test()
    elif TEST == False:
        main()