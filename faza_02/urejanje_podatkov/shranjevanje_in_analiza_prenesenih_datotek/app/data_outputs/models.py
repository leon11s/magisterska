from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.dialects.mysql import LONGTEXT

from helpers.config_reader import *

Base = declarative_base()

class File(Base):
    __tablename__ = DB_OUTPUT_TABLE_NAME
    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    parent_id = Column(Integer)
    file_name = Column(String(200))
    md5_hash = Column(String(50), index=True)
    file_size_kb = Column(Float)
    is_text_file = Column(Boolean)
    file_type = Column(String(100))
    sha256_hash = Column(String(100), index=True)
    sha1_hash = Column(String(100), index=True)
    virus_total_infections_count = Column(Integer)
    virus_total_report = Column(LONGTEXT)
    virus_total_tokens = Column(LONGTEXT)
    file_path = Column(String(50), index=True)

