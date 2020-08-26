import re
from typing import List

from helpers.printer import print_debug

def find_unique_urls(data) -> List:
    '''
    Returns a list of unique-URLs in the dataframe.
    '''
    results = data.copy()
    results = regex_search(results, r'wget|curl|lwp-download', how='contains', column_name='urls')
    urls_results = results[results['urls'] == True].copy()
    urls_results.drop(columns='urls', inplace=True)
    urls_results.drop_duplicates('command', inplace=True)

    wget_unique = get_wget_urls(urls_results)
    curl_unique = get_curl_urls(urls_results)
    lwp_download_unique = get_lwp_download_urls(urls_results)

    unique_urls_lsit = []
    unique_urls_lsit.extend(wget_unique)
    unique_urls_lsit.extend(curl_unique)
    unique_urls_lsit.extend(lwp_download_unique)

    unique_urls = list(set(unique_urls_lsit))
    print_debug(f'We found {len(unique_urls)} unique URLs.')

    unique_urls = validate_adn_fix_urls(unique_urls)
    
    return unique_urls

def regex_search(data, pattern, column_name, how='match', override=False):
    TEMP_COLUMN = 'temp'
    regex_compiled = re.compile(pattern)
    if how == 'match':
        data[TEMP_COLUMN] = data['command'].str.match(regex_compiled, case=True)
    elif how == 'contains':
        data[TEMP_COLUMN] = data['command'].str.contains(regex_compiled, case=True, regex=True)
    
    if override == False:
        try:
            data[column_name] = data[column_name] | data[TEMP_COLUMN]
        except KeyError:
            data[column_name] = data[TEMP_COLUMN]
    elif override == True:
        data[column_name] = data[TEMP_COLUMN]
    data.drop(columns=[TEMP_COLUMN], inplace=True)
    return data

def get_wget_urls(data) -> List:
    #regex izloči vse URL-je ki se ponovijo po wget-u
    wget_urls = data['command'].str.extractall(r'wget\s-?c?-?q?\s?(?P<wget_urls>[\w\d\.\/\-:]+)').reset_index(level=['session'])
    # odstranimo vse tiste vrstice, ki ne vsebujejo url-ja (nimajo pike)
    wget_urls = wget_urls[wget_urls['wget_urls'].str.contains(r'\.')]
    return wget_urls['wget_urls'].unique().tolist()

def get_curl_urls(data) -> List:
    #regex izloči vse URL-je ki se ponovijo po curl-u
    curl_urls = data['command'].str.extractall(r'curl\s-?O?\s?(?P<curl_urls>[\w\d\.\/\-:]+)').reset_index(level=['session'])
    # odstranimo vse tiste vrstice, ki ne vsebujejo url-ja (nimajo pike)
    curl_urls = curl_urls[curl_urls['curl_urls'].str.contains(r'\.')]
    return curl_urls['curl_urls'].unique().tolist()

def get_lwp_download_urls(data) -> List:
    #regex izloči vse URL-je ki se ponovijo po lwp_download-u
    lwp_download_urls = data['command'].str.extractall(r'lwp_download\s?(?P<lwp_download>[\w\d\.\/\-:]+)').reset_index(level=['session'])
    # odstranimo vse tiste vrstice, ki ne vsebujejo url-ja (nimajo pike)
    lwp_download_urls = lwp_download_urls[lwp_download_urls['lwp_download'].str.contains(r'\.')]
    return lwp_download_urls['lwp_download'].unique().tolist()

def validate_adn_fix_urls(urls):
    fixed_urls = []
    # regex for matching a valid url
    pattern_full = re.compile(r'(\b(https?|ftp|file)://)[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
    pattern_domain = re.compile(r'[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
    for url in urls:
        if pattern_full.match(url):
            print_debug(f'[OK] URL: {url} is valid!')
            fixed_urls.append(url)
        elif pattern_domain.search(url):
            print_debug(f'--> Trying to fix url: {url}.')
            new_url_http = f'http://{url}'
            if pattern_full.match(new_url_http):
                print_debug(f'[OK] URL fixed: {new_url_http} is valid!')
                fixed_urls.append(new_url_http)
            
            # new_url_https = f'https://{url}'
            # if pattern_full.match(new_url_https):
            #     print_debug(f'[OK] URL fixed: {new_url_https} is valid!')
            #     fixed_urls.append(new_url_https)
        else:
            print_debug(f'[X] URL: {url} is NOT fixable and valid!')
    return fixed_urls