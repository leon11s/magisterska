import hashlib

from helpers.config_reader import *

def get_file_hash_md5(filename:str, hex_string:bool=True):
    path = f'./app/{GENERAL_FILES_FOLDER}/{filename}'
    file_iter = file_as_blockiter(open(path, 'rb'))
    return hash_bytestr_iter(file_iter, hashlib.md5(), ashexstr=hex_string)
    
def get_file_hash_sha256(filename:str, hex_string:bool=True):
    path = f'./app/{GENERAL_FILES_FOLDER}/{filename}'
    file_iter = file_as_blockiter(open(path, 'rb'))
    return hash_bytestr_iter(file_iter, hashlib.sha256(), ashexstr=hex_string)

def get_file_hash_sha1(filename:str, hex_string:bool=True):
    path = f'./app/{GENERAL_FILES_FOLDER}/{filename}'
    file_iter = file_as_blockiter(open(path, 'rb'))
    return hash_bytestr_iter(file_iter, hashlib.sha1(), ashexstr=hex_string)

def hash_bytestr_iter(bytesiter, hasher, ashexstr=True):
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest() if ashexstr else hasher.digest()

def file_as_blockiter(afile, blocksize=65536):
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)


