import requests
import time
import re
import json
from collections import Counter

from helpers.printer import print_debug
from helpers.config_reader import SERVICES_VIRUS_TOTAL_API_KEY

def get_report(md5_hash:str):
    data = download_report(md5_hash)
    if data == False:
        return (0, 'NOT FOUND', None)
    elif data:
        detections = malicious_counter_parser(data)
        reports = malicious_report_parser (data)
        tokens = tokanizer(reports)
        return (detections, reports, tokens)
    else:
        return (None, None, None)


def tokanizer(text, most_common = 4):
    text = text.lower()
    text = re.split('[^a-zA-Z]', text)
    text = [x for x in text if x]
    tokens = Counter(text).most_common(most_common)
    return json.dumps(tokens)


def malicious_report_parser(data):
    data = data.get('data').get('attributes').get('last_analysis_results')
    try:
        result = [value.get('result') for _, value in data.items()]
        result = [x for x in result if x is not None]
        return '|'.join(list(set(result))) 
    except Exception as err:
        print_debug(f'Error occurred: {err}')
        return None


def malicious_counter_parser(data):
    try:
        data = data.get('data').get('attributes').get('last_analysis_results')
        detection_status = [value.get('category') for _, value in data.items()]
        detections = Counter(detection_status).get('malicious')
        return detections
    except Exception as err:
        print_debug(f'Error occurred: {err}')
        return None


def download_report(hash_):
    url = f'https://www.virustotal.com/api/v3/files/{hash_}'
    header = {'x-apikey': SERVICES_VIRUS_TOTAL_API_KEY}

    try:
        response = requests.get(url, headers=header)
    except Exception as err:
        print_debug(f'[Getting URL: {url}] Other error occurred: {err}')
        return None

    status_code = response.status_code

    if status_code == 200: # success
        return response.json()
    elif status_code == 400: # BadRequestError
        error = response.json().get('error').get('message')
        print_debug(f'Virus total: BadRequestError -> {error}')
        return None
    elif status_code == 404: # NotFoundError
        error = response.json().get('error').get('message')
        print_debug(f'Virus total: NotFoundError -> {error}')
        return False
    elif status_code == 429: # QuotaExceededError
        error = response.json().get('error').get('message')
        print_debug(f'Virus total: QuotaExceededError -> {error} \nSleeping for 60s.')
        time.sleep(60) 
        return download_report(hash_) # rekruzivno kličemo dokler ne dobimo odgovora
    elif status_code == 401: # WrongCredentialsError
        error = response.json().get('error').get('message')
        print_debug(f'Virus total: WrongCredentialsError -> {error}')
        return None
    elif status_code == 503: # TransientError
        error = response.json().get('error').get('message')
        print_debug(f'Virus total: TransientError -> {error}')
        return None
    else:
        error = response.json().get('error').get('message')
        print_debug(f'Virus total: OtherError -> {error}')
        return None






