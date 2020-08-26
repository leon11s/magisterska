'''
 ## validator.py

Function for checking if the data for parsing is correct
'''
import configparser
from sqlalchemy import create_engine
import logging


config = configparser.ConfigParser(allow_no_value=True)
config.read('./cowrie-data-extractor.conf')

TABLE_NAME = str(config['OUTPUTS_DB']['TABLE_NAME'])
dialect = str(config['OUTPUTS_DB']['dialect'])
user = str(config['OUTPUTS_DB']['user'])
password = str(config['OUTPUTS_DB']['password'])
host = str(config['OUTPUTS_DB']['host'])
dbname = str(config['OUTPUTS_DB']['dbname'])


if dialect == 'sqlite':
    url = dialect + ':///' + dbname
else:
    url = dialect + '://' + user + ':' + password + '@' + host + '/' + dbname


def check_for_empty_result(result_data):
    '''
    Check if there are any sessions in the result_data.
    Returns:
    - True: ERROR: no data
    - False: OK

    '''
    if result_data['hits']['total'] == 0:
        logging.error('No sessions for this time interval.')
        return True
    else:
        return False

def check_for_session_connect_event(result_data, session):
    '''
    Check for cowrie.session.connect event in session data.
    Returns:
    - True: ERROR: no cowrie.session.connect event
    - False: OK

    '''
    for event in result_data['hits']['hits']:
        # Check for cowrie.session.connect
        if event['_source']['eventid'] == 'cowrie.session.connect':            
            return False

    # no cowrie.session.connect event found
    logging.error('No cowrie.session.connect event for session: ' + str(session))
    return True
    
def clean_duplicated_sessions(session_list_raw):
    '''
    Check if new sessions are already in the database.
    Returns:
    - returns a tuple:
        - list of sessions that are not alreay in the database
        - int: countetr of removed sessions
    '''

    counter = 0
    placeholder= '"{}"'
    duplicated_sessions = []
    placeholders= ', '.join(placeholder for _ in session_list_raw)

    session_list_raw = map(lambda s: s.strip(), session_list_raw)
    session_list_raw = tuple(list(session_list_raw))

    query = 'SELECT session FROM ' + TABLE_NAME + ' WHERE session IN (' + placeholders + ')'
    query = query.format(*session_list_raw)

    engine = create_engine(url, echo=False)

    with engine.connect() as con:
        rs = con.execute(query)
        for result in rs:
            duplicated_sessions.append(result[0])

    # clean list of sessions
    session_list_clean = [x for x in session_list_raw if x not in duplicated_sessions]

    for session in [x for x in session_list_raw if x in duplicated_sessions]:
        logging.info('Duplicated session founded. Removing session:' + str(session))
        counter += 1

    return (session_list_clean, counter) 

def check_for_max_events_per_session(result_data, max_query_size, session_id):
    if result_data['hits']['total'] > max_query_size:
        with open('./data/skipped_sessions.txt', 'a') as f:
            f.write(session_id + '\n')
        logging.error('To many events per session. Limit is:' + str(max_query_size))    
        return True
    else:
        return False


if __name__ == '__main__':
    # DEBUG CODE
    with open('./data/unique_sessions.txt', 'r') as f:
        session_ids_all = f.readlines()
        result = clean_duplicated_sessions(session_ids_all)