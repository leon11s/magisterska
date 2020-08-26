import configparser

config = configparser.ConfigParser(allow_no_value=True)
config.read('./cowrie-command-data-analysis.conf')

UNIQUE_SCRIPTS_TABLE_NAME = str(config['DB_CONF']['UNIQUE_SCRIPTS_TABLE_NAME'])
dialect = str(config['DB_CONF']['dialect'])
dbname = str(config['DB_CONF']['dbname'])
user = str(config['DB_CONF']['user'])
password = str(config['DB_CONF']['password'])
host = str(config['DB_CONF']['host'])
ALL_SCRIPTS_COLUMN_LEN = int(config['DB_CONF']['ALL_SCRIPTS_COLUMN_LEN'])
INPUT_TABLE_NAME = str(config['DB_CONF']['INPUT_TABLE_NAME'])
GENERAL_TABLE_NAME = str(config['DB_CONF']['GENERAL_TABLE_NAME'])
start_time = str(config['DEFAULT']['start_time'])
end_time = str(config['DEFAULT']['end_time'])


# GENERAL
DEBUG = config.getboolean('GENERAL', 'DEBUG')
PRINT_INFO = config.getboolean('GENERAL', 'PRINT_INFO')
REALTIME_MODE = config.getboolean('GENERAL', 'REALTIME_MODE')

# FILTER
FILTER_LOCAL_IP = config.getboolean('FILTER', 'FILTER_LOCAL_IP')
FILTER_LTFE_IP = config.getboolean('FILTER', 'FILTER_LTFE_IP')


# TABLES_NAMES
FINAL_COMMAND_TABLE = str(config['TABLES_NAMES']['FINAL_COMMAND_TABLE'])