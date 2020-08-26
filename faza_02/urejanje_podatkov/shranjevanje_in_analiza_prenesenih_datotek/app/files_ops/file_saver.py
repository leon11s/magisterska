import os

from helpers.config_reader import GENERAL_FILES_DB_PATH


def save_file(file_md5_hash:str, base64_file_data:str, location:str='local') -> str:
    '''
    Saves the file in base64 format to provided location.
    '''
    if location == 'local':
        return _save_file_to_local_file_system(file_md5_hash, base64_file_data)
    elif location == 'remote_server':
        print('NOT IMPLEMENTED')
        # TODO: implement
    elif location == 'aws_s3':
        print('NOT IMPLEMENTED')
        # TODO: implement
    else:
        print('Location argument does not match: local, remote_server or aws_s3.')

    
def _save_file_to_local_file_system(file_hash, data):
    file_path = _get_file_path(file_hash)
    full_path = f'{GENERAL_FILES_DB_PATH}{file_path}'
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(data)
    return file_path
    

def _get_file_path(file_hash: str) -> str:
    first_two = file_hash[:2]
    second_two = file_hash[2:4]
    return f'/{first_two}/{second_two}/{file_hash}'
