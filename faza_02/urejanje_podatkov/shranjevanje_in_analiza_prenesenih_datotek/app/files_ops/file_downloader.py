import configparser
from typing import Tuple

import requests
from requests.exceptions import Timeout
from requests.exceptions import HTTPError

from helpers.printer import print_debug

config = configparser.ConfigParser()
config.read('./app/cyberlab-files-analysis.conf')

files_folder = str(config['GENERAL']['FILES_FOLDER'])


def download_file(url:str, filename:str, timeout:int =5) -> bool:
    '''
    Downloads the file from the URL and saves it on the system. 
    Returns True if Ok, otherwise False.
    '''
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except HTTPError as http_err:
        #print_debug(f'[Getting URL: {url}] HTTP error occurred: {http_err}')
        print_debug(f'[Getting URL: {url}] HTTP error occurred.')
        return False
    except Timeout as err:
        #print_debug(f'[Getting URL: {url}] The request timed out: {err}')
        print_debug(f'[Getting URL: {url}] The request timed out.')
        return False
    except Exception as err:
        #print_debug(f'[Getting URL: {url}] Other error occurred: {err}')
        print_debug(f'[Getting URL: {url}] Other error occurred.')
        return False
    else:
        print_debug(f'[Getting URL: {url}] Successful! Status code: {response.status_code}')
        
        path = f'./app/{files_folder}/{filename}'
        with open(path, 'wb') as f:
            f.write(response.content)
        
        return True