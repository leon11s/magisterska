import configparser

from sqlalchemy import create_engine, MetaData, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from datetime import datetime

config = configparser.ConfigParser(allow_no_value=True)
config.read('./app/provider_analyzer.conf')

AS_TABLE_NAME = str(config['DB_INSERT']['AS_TABLE_NAME'])
IP_UNIQUE_TABLE = str(config['DB_INSERT']['IP_UNIQUE_TABLE'])

dialect = str(config['DB_CREDENTIALS']['dialect'])
dbname = str(config['DB_CREDENTIALS']['dbname'])
user = str(config['DB_CREDENTIALS']['user'])
password = str(config['DB_CREDENTIALS']['password'])
host = str(config['DB_CREDENTIALS']['host'])

def parse_database_connection_url(dialect, dbname, host, user, password):
    if dialect == 'sqlite':
        url = dialect + ':///' + dbname
    else:
        url = dialect + '://' + user + ':' + password + '@' + host + '/' + dbname

    return url

url = parse_database_connection_url(dialect, dbname, host, user, password)
engine = create_engine(url, echo=False)
Base = declarative_base()

class ASTable(Base):
    __tablename__ = AS_TABLE_NAME
    asn = Column(Integer, primary_key=True, autoincrement=False)
    as_rir = Column(String(10), index=True)
    as_name = Column(String(300), index=True)
    as_route = Column(String(200))
    as_num_addresses = Column(Integer)
    as_description = Column(String(200))
    as_prefix_description = Column(String(200))
    as_abuse_contact_email = Column(String(200))
    as_count = Column(Integer)
    timestamp_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    timestamp_created = Column(DateTime, default=datetime.now)
    ip_relation = relationship("IPTable", back_populates="as_relation")


class IPTable(Base):
    __tablename__ = IP_UNIQUE_TABLE
    ip = Column(String(16), primary_key=True)
    ip_count = Column(Integer)
    ip_city = Column(String(100))
    ip_country_name = Column(String(60), index=True)
    ip_longitude = Column(Float)
    ip_latitude = Column(Float)
    ip_hostname = Column(String(100))
    timestamp_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    timestamp_created = Column(DateTime, default=datetime.now)
    asn_id = Column(Integer, ForeignKey(AS_TABLE_NAME+'.asn'))
    as_relation = relationship("ASTable", back_populates="ip_relation") 


def create_tables_if_not_exist(engine):
    if (not engine.dialect.has_table(engine, AS_TABLE_NAME) or 
        not engine.dialect.has_table(engine, IP_UNIQUE_TABLE)):
            ASTable.metadata.create_all(engine)
            IPTable.metadata.create_all(engine)

def ip_in_local_database(session, ip_):
    exists = session.query(IPTable.ip).filter_by(ip=str(ip_)).scalar() is not None
    if not exists:
        return False
    else:
        return True

def increment_ip_count(session, ip_):
    #posodobimo vrednost v IP tabeli
    session.query(IPTable).filter_by(ip=str(ip_)).update({'ip_count': IPTable.ip_count + 1})

    #posodobimo podatke v AS tabeli
    asn_val = session.query(IPTable.asn_id).filter_by(ip=ip_).scalar()
    session.query(ASTable).filter_by(asn=asn_val).update({'as_count': ASTable.as_count + 1})
    session.commit()    

def add_update_row_as(session, data_object):
    new_row_object = ASTable(asn = data_object.as_asn,
                    as_rir = data_object.as_rir,
                    as_name = data_object.as_name,
                    as_route = data_object.as_route,
                    as_num_addresses = data_object.as_num_addresses,
                    as_description = data_object.as_description,
                    as_prefix_description = data_object.as_prefix_description,
                    as_abuse_contact_email = data_object.as_abuse_contact_email,
                    as_count = 1)

    filter_value = data_object.as_asn

    exists = session.query(ASTable.asn).filter_by(asn=str(filter_value)).scalar() is not None
    if not exists:
        session.add(new_row_object)
        session.commit()
    else:
        session.query(ASTable).filter_by(asn=new_row_object.asn).update({'as_count': ASTable.as_count + 1})
        session.commit()
    return exists


def add_update_row_ip(session, data_object):
    new_row_object = IPTable(ip = data_object.ip,
                ip_city = data_object.city,
                ip_country_name = data_object.country_name,
                ip_longitude = data_object.longitude,
                ip_latitude = data_object.latitude,
                ip_hostname = data_object.hostname,
                asn_id = data_object.as_asn,
                ip_count = 1)

    filter_value = data_object.as_asn

    exists = session.query(IPTable.ip).filter_by(ip=str(filter_value)).scalar() is not None
    if not exists:
        session.add(new_row_object)
        session.commit()
    else:
        session.query(IPTable).filter_by(ip=new_row_object.ip).update({'ip_count': IPTable.ip_count + 1})
        session.commit()
    return exists    
 

