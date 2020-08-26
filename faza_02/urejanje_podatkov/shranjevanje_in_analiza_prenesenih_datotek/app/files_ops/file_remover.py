import os
import glob

from helpers.config_reader import GENERAL_FILES_FOLDER

def remove_temp_files():
    files = glob.glob(f'./app/{GENERAL_FILES_FOLDER}/*')
    for f in files:
        os.remove(f)
