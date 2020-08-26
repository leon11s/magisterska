import pandas as pd
from sqlalchemy import create_engine

from helpers.printer import print_debug
from helpers.config_reader import (DB_INPUT_DB_URL, 
                                   DB_INPUT_TABLE_NAME,
                                   DB_INPUT_COLUMNS)


engine= create_engine(DB_INPUT_DB_URL)

def read_sql_table(limit:int = 500, min_id:int = 0, index:str='session'):
    SQL_QUERY = f'SELECT {",".join(DB_INPUT_COLUMNS)} FROM {DB_INPUT_TABLE_NAME} WHERE id > {min_id} LIMIT {str(limit)};'
    data = pd.read_sql_query(SQL_QUERY, engine)
    data.set_index(index, inplace=True)
    print_debug(f'Getting table: {DB_INPUT_TABLE_NAME} with shape: {data.shape[0]} x {data.shape[1]}')
    return data
