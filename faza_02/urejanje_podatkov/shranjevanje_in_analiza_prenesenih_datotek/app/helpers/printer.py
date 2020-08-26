import configparser

config = configparser.ConfigParser()
config.read('./app/cyberlab-files-analysis.conf')
DEBUG = bool(config['GENERAL']['DEBUG'])

def print_debug(s:str):
    if DEBUG:
        print(s)