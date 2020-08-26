import configparser
import json

config = configparser.ConfigParser()
config.read('./app/cyberlab-files-analysis.conf')


# --- GENERAL --- #
general_conf = config['GENERAL']
GENERAL_MODE = str(general_conf.get('MODE', 'batch'))

# --- DB_INPUT --- #
db_input_conf = config['DB_INPUT']
DB_INPUT_DB_URL = str(db_input_conf.get('db_url', 'none'))
DB_INPUT_TABLE_NAME = str(db_input_conf.get('table_name', 'none'))
DB_INPUT_COLUMNS = json.loads(db_input_conf.get('columns', 'none'))
DB_INPUT_LIMIT = int(db_input_conf.get('limit', 1))
DB_INPUT_START_ID = int(db_input_conf.get('start_id', 0))



GENERAL_FILES_FOLDER = str(config['GENERAL']['FILES_FOLDER'])
GENERAL_FILES_DB_PATH = str(config['GENERAL']['FILES_DB_PATH'])

DB_OUTPUT_DB_URL = str(config['DB_OUTPUT']['db_url'])
DB_OUTPUT_TABLE_NAME = str(config['DB_OUTPUT']['table_name'])
SERVICES_VIRUS_TOTAL_API_KEY = str(config['SERVICES']['virus_total_api_key'])


