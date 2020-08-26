from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean

from database import parse_database_connection_url
from config_reader import dialect, dbname, user, password, host, UNIQUE_SCRIPTS_TABLE_NAME, ALL_SCRIPTS_COLUMN_LEN


url = parse_database_connection_url(dialect, dbname, host, user, password)
engine = create_engine(url, echo=False)
Base = declarative_base()

# ALL_SCRIPTS_TABLE
print('Creating table:', UNIQUE_SCRIPTS_TABLE_NAME)
class CowrieLoginData(Base):
    __tablename__ = UNIQUE_SCRIPTS_TABLE_NAME

    id = Column(Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    commands_string = Column(String(ALL_SCRIPTS_COLUMN_LEN))
    repetitions_count = Column(Integer)

Base.metadata.create_all(engine)