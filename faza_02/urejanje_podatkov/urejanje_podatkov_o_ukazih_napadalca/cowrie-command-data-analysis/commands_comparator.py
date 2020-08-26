from difflib import SequenceMatcher
from database import SQLDatabaseInput

class CommandsComparator():
    @staticmethod
    def is_script_automated(commands_string, diff_ratio_speed_mode='r'):
        similarity_diff_ratio = CommandsComparator.get_similarity_ratio(commands_string, 'enable', method=diff_ratio_speed_mode)
        return similarity_diff_ratio

    @staticmethod
    def is_script_in_database(str1, engine, method='ratio'):
        all_scripts_data = engine.get_all_scripts_list()

        candidates_list = []

        for script in all_scripts_data:
            ratio = CommandsComparator.get_similarity_ratio(str1, script[1], method)
            if ratio > 0.55:
                candidates_list.append((script, ratio))
            

        if not candidates_list:
            is_in_database = False
            database_id = None
        else:
            is_in_database = True
            best_choice = max(candidates_list, key=lambda x: x[1])
            database_id = best_choice[0][0]


        return (is_in_database, database_id)
          

    @staticmethod
    def get_similarity_ratio(str1, str2, method='ratio'):
        '''
        Return a measure of the sequences’ similarity as a float in the range [0, 1].
        Where T is the total number of elements in both sequences, and M is the number of matches, this is 2.0*M / T. 
        Note that this is 1.0 if the sequences are identical, and 0.0 if they have nothing in common.
        '''
        if method == 'ratio' or method == 'r':
            return SequenceMatcher(None, str1, str2).ratio()
        elif method == 'quick_ratio' or method == 'qr':
            return SequenceMatcher(None, str1, str2).quick_ratio()
        elif method == 'real_quick_ratio' or method == 'rqr':
            return SequenceMatcher(None, str1, str2).real_quick_ratio()
        else:
            raise ValueError('ERROR in CommandsComparator.get_similarity_ratio(): parameter method wrong. Use r, qr or rqr')


    


        



    