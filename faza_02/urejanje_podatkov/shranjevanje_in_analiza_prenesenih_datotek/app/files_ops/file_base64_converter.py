import base64

from helpers.config_reader import *

def encode_file(filename: str) -> str:
    path = f'./app/{GENERAL_FILES_FOLDER}/{filename}'
    with open(path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()

    return encoded_string


