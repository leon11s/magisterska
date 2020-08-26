#!/usr/bin/env python3

import parsers
import itertools
import configparser
import logging
import datetime

from database import SQLDatabaseInput, SQLDatabaseOutput
from commands_comparator import CommandsComparator
from patterns import check_pattern
from helper_functions import append_session_id_to_file, remove_inserted_sessions, get_round_times
from insert_final_table import InsertFinalCommandTable

from config_reader import (UNIQUE_SCRIPTS_TABLE_NAME, FILTER_LOCAL_IP, ALL_SCRIPTS_COLUMN_LEN, DEBUG, PRINT_INFO,
                           REALTIME_MODE, FILTER_LTFE_IP, start_time, end_time)
 

class CowrieCommandDataAnalysis():
    def __init__(self, table_name, realtime=False, print_info=True, debug=False, **kwargs):
        '''
        The InsertToUniqueScriptTable object creates a table with unique scripts.

        Args:
            table_name (str): name of the table to insert unique scripts
            realtime (bool): if True, run in realtime mode 
            **kwargs (bool): The keyword arguments are used for filtering
                - local_ips_filter: insert local ips, strting with 10.
                - ltfe_ips_filter: insert ltfe ips: 212.235.185.131
        '''
        self.unique_script_table_name = table_name
        self.realtime_mode = realtime
        self.debug = debug
        self.print_info = print_info
        self.local_ips_filter = False
        self.ltfe_ips_filter = False

        # filters configiration
        if kwargs is not None:
            for filter_name, filter_state in kwargs.items():
                if type(filter_state) == bool:
                    if filter_name == 'local_ips':
                        self.local_ips_filter = filter_state
                    elif filter_name == 'ltfe_ips':
                        self.ltfe_ips_filter = filter_state
                    else:
                        continue
                else:
                    raise TypeError('Filter value must be bool: False/True')

        # connect to database
        self.db_engine_input = SQLDatabaseInput()
        self.db_engine_output = SQLDatabaseOutput()            

        if self.realtime_mode == True:
            if self.debug: print('Running in realtime mode...')
            self.sessions = self._get_sessions_realtime_mode()
        else:
            if self.debug: print('Running in normal mode...')
            self.sessions = self._get_sessions_normal_mode()

        # Check if table with unique scripts is empty
        self.unique_script_table_is_empty = self.db_engine_output.is_all_script_table_empty()

        # Print InsertToUniqueScriptTable info
        if self.print_info:
            self._print_init_config()

        # Insert data to final table
        self.final_table_conn = InsertFinalCommandTable()    

    def _print_init_config(self):
        print(f'*-----------------------------------*')
        print(f'* MakeUniqueScriptTable initialized *')
        print(f'table_name = {self.unique_script_table_name}')
        print(f'realtime = {self.realtime_mode}')
        print(f'local_ips = {self.local_ips_filter}')
        print(f'ltfe_ips = {self.ltfe_ips_filter}')    
        print(f'*-----------------------------------*')

    def _get_sessions_realtime_mode(self):
        '''
        Get sessions for realtime mode.
        '''
        t_start, t_end = get_round_times(dt=None, date_delta=datetime.timedelta(minutes=10), to='down', interval=70)
        all_sessions = self.db_engine_input.get_session_ids(t_start, t_end)
        if self.debug: print(f'Time interval from {t_start} to {t_end}.')
        if self.debug: print('Number of all sessions:', len(all_sessions))
        sessions = remove_inserted_sessions(all_sessions)
        if self.debug: print('Nmber of session to analize:', len(sessions))
        return sessions

    def _get_sessions_normal_mode(self):
        '''
        Get sessions for normal mode.
        '''
        all_sessions = self.db_engine_input.get_session_ids(start_time, end_time)
        if self.debug: print(f'Time interval from {start_time} to {end_time}.')
        if self.debug: print('Number of all sessions:', len(all_sessions))
        sessions = remove_inserted_sessions(all_sessions)
        if self.debug: print('Nmber of session to analize:', len(sessions))
        return sessions

    def _check_and_filter_ip(self, ip, session):
        if ip == None: # check if IP field is empty
            if self.debug: print('No SRC_IP for session: ', session)
            append_session_id_to_file(session)
            return True
        elif self.local_ips_filter and (ip.startswith('10.') or ip.startswith('192.168.')): # Filter local IPs
            append_session_id_to_file(session)
            return True
        elif self.ltfe_ips_filter and ip == '212.235.185.131': # Filter LTFE IPs
            append_session_id_to_file(session)
            return True
        else:
            return False

    def _get_validated_commands_for_session(self, session):
        command_data = self.db_engine_input.get_command_data(session)
        number_of_commands = command_data[0][1]
        command_str = ''
        for command in command_data:
            command_str += (command[2]+ '\n') 

        # Check if data is too long for insert in table
        command_str_len = len(command_str)
        if command_str_len >= ALL_SCRIPTS_COLUMN_LEN:
            if self.debug: print('ERROR: Command_str too long! Lenght:', command_str_len, 'Session:', session)
            append_session_id_to_file(session)
            append_session_id_to_file(session, file_name='output_data/too_long_sessions')
            return False

        if self.debug: print('---------')
        if self.debug: print('Session:', session)
        if self.debug: print('Number of commands', number_of_commands)
        # if self.debug: print('Commands: ', command_str)
        return command_str 

    def insert_to_database(self):
        for session in self.sessions:
            # get ip for session
            src_ip = self.db_engine_input.get_src_ip_from_session(session)

            # filter and check IP
            if self._check_and_filter_ip(src_ip, session):
                continue

            # get commands for session
            command_str = self._get_validated_commands_for_session(session) 
            if command_str == False:
                continue

            # If table with unique scripts is empty add first script to database
            if self.unique_script_table_is_empty:
                self.db_engine_output.insert_new_script_to_all_scripts_table(command_str)
                self.unique_script_table_is_empty = False
                append_session_id_to_file(session)
                continue

            # Check if command script already in database
            is_script_in_database_bool, database_id = CommandsComparator.is_script_in_database(command_str, engine=self.db_engine_input)  
            if is_script_in_database_bool:
                # Update counter (+1) if script already in table
                self.db_engine_output.add_one_to_counter(database_id)
                if self.debug: print('--> INFO: Updating repetitions_count (adding 1), to ID:', database_id)
            else:
                # Add new script to database
                database_id = self.db_engine_output.insert_new_script_to_all_scripts_table(command_str)
                if self.debug: print('--> INFO: Adding new script to database with ID:', database_id)

            self.final_table_conn.insert_to_table(session, src_ip, database_id)

            append_session_id_to_file(session)



if __name__ == "__main__":
    command_data = CowrieCommandDataAnalysis(UNIQUE_SCRIPTS_TABLE_NAME, 
                                                    realtime=REALTIME_MODE, 
                                                    print_info=PRINT_INFO, 
                                                    debug=DEBUG, 
                                                    local_ips=FILTER_LOCAL_IP, 
                                                    ltfe_ips=FILTER_LTFE_IP)

    command_data.insert_to_database()
    
    print('---------->FINISHED<-----------')
