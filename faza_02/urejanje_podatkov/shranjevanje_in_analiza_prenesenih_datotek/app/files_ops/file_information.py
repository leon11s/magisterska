import re
import os
import sys
import configparser
from pathlib import Path
import mimetypes

import requests

config = configparser.ConfigParser()
config.read('./app/cyberlab-files-analysis.conf')

files_folder = str(config['GENERAL']['FILES_FOLDER'])


def get_file_name(url:str) -> str:
    AFTER_LAST_SLASH_REGEX = re.compile(r'\/([^\/]+)$')
    filename = AFTER_LAST_SLASH_REGEX.search(url)
    if filename:
        return filename.group(1)
    else:
        return "no_name.txt"


def get_file_size(filename:str, unit:str='MB') -> int:
    '''Returns the size of the file.
    
    Arguments:
    filename -- name of the file
    unit -- size unit of the response B, KB, MB (default KB)
    '''
    path = f'./app/{files_folder}/{filename}'
    size = Path(path).stat().st_size

    if unit == 'KB':
        size = size/1024
    elif unit == 'MB':
        size = size/1024/1024
    return round(size, 3)


def get_file_type(filename:str) -> str:
    path = f'./app/{files_folder}/{filename}'
    file_type, _ = mimetypes.guess_type(path)
    return file_type


def is_textfile(filename:str, blocksize:int=512) -> bool:
    """ Uses heuristics to guess whether the given file is text or binary,
        by reading a single block of bytes from the file.
        If more than 30% of the chars in the block are non-text, or there
        are NUL ('\x00') bytes in the block, assume this is a binary file.
    """
    path = f'./app/{files_folder}/{filename}'

    with open(path, 'rb') as fileobj:
        block = fileobj.read(blocksize)

    PY3 = sys.version_info[0] == 3
    # A function that takes an integer in the 8-bit range and returns
    # a single-character byte object in py3 / a single-character string
    # in py2.
    
    int2byte = (lambda x: bytes((x,))) if PY3 else chr

    _text_characters = (
            b''.join(int2byte(i) for i in range(32, 127)) +
            b'\n\r\t\f\b')

    if b'\x00' in block:
        # Files with null bytes are binary
        return False
    elif not block:
        # An empty file is considered a valid text file
        return True

    # Use translate's 'deletechars' argument to efficiently remove all
    # occurrences of _text_characters from the block
    nontext = block.translate(None, _text_characters)
    return float(len(nontext)) / len(block) <= 0.30


# def get_virus_total_data(md5_hash):
#     url = f'https://www.virustotal.com/api/v3/files/{md5_hash}'
#     requests.get(url)
