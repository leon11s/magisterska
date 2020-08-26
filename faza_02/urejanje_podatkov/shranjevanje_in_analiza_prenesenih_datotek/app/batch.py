import logging

from analyze_url import analyze_url
from data_inputs import get_sql_data
from urls_ops import unique_url_parser
from helpers.config_reader import DB_INPUT_LIMIT, DB_INPUT_START_ID


logger = logging.getLogger('cyberlab_files_analysis.batch')

def run_batch_mode():
    #Gets command data from SQL-table
    commands = get_sql_data.read_sql_table(limit=DB_INPUT_LIMIT, min_id=DB_INPUT_START_ID, index='session')

    # TODO: poišči vse url-je, ki so skriti v base64 encodingu -> implementiraj v find unique ip funkcijo -> premakni v posebni modul
    urls = unique_url_parser.find_unique_urls(commands)

    logger.info('Starting analyzing URLs.')
    for url in urls:
        analyze_url(url)

    


