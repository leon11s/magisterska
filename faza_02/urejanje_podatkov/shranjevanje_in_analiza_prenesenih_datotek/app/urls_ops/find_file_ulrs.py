import re
from typing import List

from .unique_url_parser import validate_adn_fix_urls
from helpers.config_reader import GENERAL_FILES_FOLDER


def get_urls(filename: str)-> List:
    path = f'./app/{GENERAL_FILES_FOLDER}/{filename}'
    urls = []
    pattern_wget = re.compile(rb'wget\s-?c?-?q?\s?(?P<wget_urls>[\w\d\.\/\-:]+)')
    pattern_curl = re.compile(rb'curl\s-?O?\s?(?P<curl_urls>[\w\d\.\/\-:]+)')
    pattern_lwp = re.compile(rb'lwp_download\s?(?P<lwp_download>[\w\d\.\/\-:]+)')

    pattern_x86 = re.compile(rb'X86="(.+)"')
    pattern_arm = re.compile(rb'ARM="(.+)"')
    pattern_aarch64 = re.compile(rb'AARCH64="(.+)"')


    
    with open(path, 'rb') as f:
        for line in f:
            # find wget
            for match in re.finditer(pattern_wget, line):
                urls.append(match.group(1).decode())
            
            # find curl
            for match in re.finditer(pattern_curl, line):
                urls.append(match.group(1).decode())
                
            # find lwp
            for match in re.finditer(pattern_lwp, line):
                urls.append(match.group(1).decode())

            for match in re.finditer(pattern_x86, line):
                urls.append(match.group(1).decode())

            for match in re.finditer(pattern_arm, line):
                urls.append(match.group(1).decode())

            for match in re.finditer(pattern_aarch64, line):
                urls.append(match.group(1).decode())
            
          
    
    urls = list(set(urls))  # extract unique urls
    urls = validate_adn_fix_urls(urls)
    return urls
