from typing import Dict

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from helpers.config_reader import *
from helpers.printer import print_debug
from data_outputs.models import File


engine= create_engine(DB_OUTPUT_DB_URL)
Session = sessionmaker(bind=engine)
session = Session()


def insert_data(data: Dict, index:str, mode='append'):
    df = pd.DataFrame.from_dict(data, orient='columns')
    df.set_index(index, inplace=True)
    df.to_sql(name=DB_OUTPUT_TABLE_NAME, con=engine, if_exists=mode)
    print_debug(f'{df.shape[0]} rows inserted to table {DB_OUTPUT_TABLE_NAME}')
    session.commit()


def create_tables_if_not_exist(engine):
    if not engine.dialect.has_table(engine, DB_OUTPUT_TABLE_NAME):
            File.metadata.create_all(engine)


def hash_exists(hash_: str) -> bool:
    exists = session.query(File.md5_hash).filter_by(md5_hash=str(hash_)).first()
    if exists:
        return True
    else:
        return False

def get_file_id(hash_:str) -> int:
    file_id = session.query(File).filter_by(md5_hash=str(hash_)).first().id
    return int(file_id)


# PREVERIMO ALI TABELE OBSTAJAJO, ČE NE JIH USTVARIMO
create_tables_if_not_exist(engine)