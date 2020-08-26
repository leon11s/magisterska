#!/usr/bin/env python3
'''
cowrie_parser.py

Main script for running the Cowrie parser.
'''
import configparser
import pandas as pd
import sys
import datetime
import logging



from parser_helpers import SessionParser, DataParser, parse_time_intervals, get_round_times
from search_queries import ElasticsearchQueries
from outputs import SQLDatabaseOutput
import validator

logging.basicConfig(level=logging.WARNING, filename='data/app.log', filemode='a')

# LOAD CONFIGURATION VARIABLES
config = configparser.ConfigParser()
config.read('./cowrie-data-extractor.conf')

elasticsearch_ip = str(config['ELASTICSEARCH']['host_ip'])
elasticsearch_port = int(config['ELASTICSEARCH']['host_port'])
elasticsearch_max_query_result_size = int(config['ELASTICSEARCH']['MAX_QUERY_RESULT_SIZE'])
elasticsearch_index = str(config['ELASTICSEARCH']['INDEX'])

program_mode = str(config['DEFAULT']['mode'])
start_time_old_data = str(config['MODE-OLD-DATA']['start_time'])
end_time_old_data = str(config['MODE-OLD-DATA']['end_time'])
interval_old_data = int(config['MODE-OLD-DATA']['interval'])
interval_realtime_data = int(config['MODE-REALTIME']['interval'])

enable_db_output = config.getboolean('OUTPUTS_DB', 'ENABLE') 

# COUNTERS
check_for_empty_result_counter = 0
check_for_session_connect_event_counter = 0
clean_duplicated_sessions_counter = 0
check_for_max_events_per_session_counter = 0

if program_mode == 'old_data':
    parsed_intervals = parse_time_intervals(start_time_old_data, end_time_old_data, interval_old_data)

    for t_start, t_end in parsed_intervals:
        print('Parsing interval: ', t_start, '->', t_end)

        # GET SESSIONS:
        es_search = ElasticsearchQueries(elasticsearch_ip, elasticsearch_port)
        res = es_search.query_by_time(elasticsearch_index, t_start, t_end, max_query_size=elasticsearch_max_query_result_size)


        # CHECK IF THERE ARE SESSIONS
        if validator.check_for_empty_result(res):
            check_for_empty_result_counter += 1
            continue
        else:    
            # PARSE UNIQUE SESSIONS:
            session_parser = SessionParser(res, max_query_size=elasticsearch_max_query_result_size)

            print('Unique sessions: ', session_parser.get_unique_sessions_ids_count())

            session_parser.save_unique_sessions() # save unique sessions to file

            all_data = dict()

            with open('./data/unique_sessions.txt', 'r') as f:
                session_ids_all = f.readlines()

            # CHECK FOR DUPLICATED SESSIONS:
            if enable_db_output:
                session_ids_all, counter = validator.clean_duplicated_sessions(session_ids_all)
                clean_duplicated_sessions_counter += counter

            # CHECK IF SESSION LIST IS EMPTY
            if len(session_ids_all) == 0:
                print('WARNING: All data already in database.')  
                continue  


            for count, session_id_ in enumerate(session_ids_all):
                session_id_ = str(session_id_).strip()

                res = es_search.query_by_session(elasticsearch_index, t_end, session_id=session_id_, max_query_size=elasticsearch_max_query_result_size)

                # CHECK FOR NUMBER OF EVENTS IN SESSION
                if validator.check_for_max_events_per_session(res, elasticsearch_max_query_result_size, session_id_):
                    check_for_max_events_per_session_counter += 1
                    continue

                # CHECK FOR SESSION CONNECT
                if validator.check_for_session_connect_event(res, session_id_):
                    check_for_session_connect_event_counter += 1
                    continue

                data_parser = DataParser(res, session_id_)
                parsed_dict = data_parser.get_session_data()

                try:
                    if count % round((len(session_ids_all) / 20)) == 0:
                        print('#', end='')
                        sys.stdout.flush()
                except ZeroDivisionError:
                    pass

                
                # MAIN DATA
                all_data[count] = parsed_dict
            

            # print(all_data)
            data = pd.DataFrame.from_dict(all_data, orient='index')
            data.set_index('session', inplace=True)
            # print(data)
            print()
            
            # OUTPUTS
            if enable_db_output:
                database_output = SQLDatabaseOutput()
                database_output.add_data_to_table_main(data)

    print('*************************************************************************************')
    print('Empty data intervals:', check_for_empty_result_counter)
    print('Broken sessions (no session_connect event):', check_for_session_connect_event_counter)  
    print('Number of removed dupicated sessions:', clean_duplicated_sessions_counter)
    print('Number of removed session with too many events:', check_for_max_events_per_session_counter)
    print('*************************************************************************************')            
                

if program_mode == 'realtime':
    # Get interval to parse
    t_start, t_end = get_round_times(dt=None, date_delta=datetime.timedelta(minutes=interval_realtime_data), to='down', interval=interval_realtime_data)
    logging.warning('Parsing interval: ' + str(t_start) + '->' + str(t_end))
    # print('Parsing interval: ', t_start, '->', t_end)

    # GET SESSIONS:
    es_search = ElasticsearchQueries(elasticsearch_ip, elasticsearch_port)
    res = es_search.query_by_time(elasticsearch_index, t_start, t_end, max_query_size=elasticsearch_max_query_result_size)

    # CHECK IF THERE ARE SESSIONS
    if validator.check_for_empty_result(res):
        check_for_empty_result_counter += 1
    else:    
        # PARSE UNIQUE SESSIONS:
        session_parser = SessionParser(res, max_query_size=elasticsearch_max_query_result_size)
        logging.warning('Unique sessions: ' + str(session_parser.get_unique_sessions_ids_count()))
        
        session_parser.save_unique_sessions() # save unique sessions to file
        all_data = dict()

        with open('./data/unique_sessions.txt', 'r') as f:
            session_ids_all = f.readlines()

        # CHECK FOR DUPLICATED SESSIONS:
        if enable_db_output:
            session_ids_all, counter = validator.clean_duplicated_sessions(session_ids_all)
            clean_duplicated_sessions_counter += counter

        # CHECK IF SESSION LIST IS EMPTY
        if len(session_ids_all) == 0:
            logging.warning('realtime_mode: All data already in database. Terminating program...')
            sys.exit()

        for count, session_id_ in enumerate(session_ids_all):
            session_id_ = str(session_id_).strip()
            res = es_search.query_by_session(elasticsearch_index, t_end, session_id=session_id_, max_query_size=elasticsearch_max_query_result_size)

            # CHECK FOR NUMBER OF EVENTS IN SESSION
            if validator.check_for_max_events_per_session(res, elasticsearch_max_query_result_size, session_id_):
                check_for_max_events_per_session_counter += 1
                continue

            # CHECK FOR SESSION CONNECT
            if validator.check_for_session_connect_event(res, session_id_):
                check_for_session_connect_event_counter += 1
                continue

            data_parser = DataParser(res, session_id_)
            parsed_dict = data_parser.get_session_data()

            # MAIN DATA
            all_data[count] = parsed_dict    

        data = pd.DataFrame.from_dict(all_data, orient='index')
        data.set_index('session', inplace=True)

        # OUTPUTS
        if enable_db_output:
            database_output = SQLDatabaseOutput()
            database_output.add_data_to_table_main(data)
            
    logging.warning('Empty data intervals:' + str(check_for_empty_result_counter))
    logging.warning('Broken sessions (no session_connect event):'+ str(check_for_session_connect_event_counter)) 
    logging.warning('Number of removed dupicated sessions:'+ str(clean_duplicated_sessions_counter))
    logging.warning('Number of removed session with too many events:'+ str(check_for_max_events_per_session_counter))