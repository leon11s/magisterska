import configparser
import requests
import logging

import ipinfo
from ipinfo.exceptions import RequestQuotaExceededError

config = configparser.ConfigParser(allow_no_value=True)
config.read('./app/provider_analyzer.conf')

logging.basicConfig(
    filename='app.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.ERROR,
    datefmt='%Y-%m-%d %H:%M:%S')


class GetBGPViewAPI:
    '''
    Get data from https://bgpview.io/ API. 
    More info about the API: https://bgpview.docs.apiary.io/#
    '''
    def __init__(self):
        self.as_route = None
        self.as_name = None
        self.as_asn = None
        self.as_description = None
        self.as_prefix_description = None
        self.as_abuse_contact_email = None

    def get_data(self, ip):
        #IP/View IP Address Details
        url = 'https://api.bgpview.io/ip/'
        full_url = url + ip
        try: 
            resp = requests.get(url=full_url)
            data = resp.json()
        except:
            error_message = '[' + ip + '] ' + 'GetBGPViewAPI: Request failed for BGPViewAPI'
            logging.error(error_message)
        
        if (resp.status_code == 200) and data['status'] == 'ok':
            # self.as_route
            try:
                self.as_route = data['data']['rir_allocation']['prefix']
            except:
                error_message = '[' + ip + '] ' + 'GetBGPViewAPI: No as_route in GetBGPViewAPI response.'
                logging.error(error_message)

            # self.as_name
            try:
                self.as_name = data['data']['prefixes'][0]['asn']['name']
            except:
                error_message = '[' + ip + '] ' + 'GetBGPViewAPI: No as_name in GetBGPViewAPI response.'
                logging.error(error_message)

            # self.as_asn
            try:
                self.as_asn = data['data']['prefixes'][0]['asn']['asn']
            except:
                error_message = '[' + ip + '] ' + 'GetBGPViewAPI: No as_asn in GetBGPViewAPI response.'
                logging.error(error_message)

            # self.as_description
            try:
                self.as_description = data['data']['prefixes'][0]['asn']['description']
            except:
                error_message = '[' + ip + '] ' + 'GetBGPViewAPI: No as_description in GetBGPViewAPI response.'
                logging.error(error_message)

            # self.as_prefix_description
            try:
                self.as_prefix_description = data['data']['prefixes'][0]['description']
            except:
                error_message = '[' + ip + '] ' + 'GetBGPViewAPI: No as_prefix_description in GetBGPViewAPI response.'
                logging.error(error_message)
            
            self._get_abuse_contact(ip)

        else:
            error_message = '[' + ip + '] ' + 'GetBGPViewAPI: get_data error. Status code: ' + str(resp.status_code) + ' Data status: ' + data['status']
            logging.error(error_message)

    def _get_abuse_contact(self, ip):
        #ASN/View ASN Details
        url = 'https://api.bgpview.io/asn/'
        full_url = url + str(self.as_asn)
        try: 
            resp = requests.get(url=full_url)
            data = resp.json()
        except:
            error_message = '[' + ip + '] ' + 'GetBGPViewAPI: Request failed for BGPViewAPI:_get_abuse_contact'
            logging.error(error_message)
        
        if (resp.status_code == 200) and data['status'] == 'ok':
            # self.as_abuse_contact_email
            try:
                self.as_abuse_contact_email = data['data']['abuse_contacts'][0]
            except:
                error_message = '[' + ip + '] ' + 'GetBGPViewAPI: No as_abuse_contact_email in GetBGPViewAPI response.'
                logging.error(error_message)
        else:
            error_message = '[' + ip + '] ' + 'GetBGPViewAPI: _get_abuse_contact error. Status code: ' + str(resp.status_code) + ' Data status: ' + data['status']
            logging.error(error_message)
        

class GetIpinfoAPI:
    '''
    Get data from https://ipinfo.io API. 
    More info about the API: https://github.com/ipinfo/python
    '''
    def __init__(self):
        self.access_token = str(config['IPINFO_API']['ACCESS_TOKEN_1'])
        self.handler = ipinfo.getHandler(self.access_token)
        self.city = None
        self.country_name = None
        self.longitude = None
        self.latitude = None
        self.hostname = None
        self.as_asn = None
        self.as_name = None

    def get_data(self, ip):
        try:
            details = self.handler.getDetails(ip)
        except RequestQuotaExceededError:
            error_message = '[' + ip + '] ' + 'GetIpinfoAPI: 50000 request limit passed!'
            logging.error(error_message)
        except:
            error_message = '[' + ip + '] ' + 'Error in connection to IPinfo API.'
            logging.error(error_message)

        # Geo data
        try:  
            self.city = details.city
        except AttributeError:
            error_message = '[' + ip + '] ' + 'GetIpinfoAPI: No city in GetIpinfoAPI response.'
            logging.error(error_message)
            self.city = None

        try: 
            self.country_name = details.country_name
        except AttributeError:
            error_message = '[' + ip + '] ' + 'GetIpinfoAPI: No country_name in GetIpinfoAPI response.'
            logging.error(error_message)
            self.country_name = None

        try:  
            self.longitude = float(details.longitude)
        except (AttributeError, TypeError):
            error_message = '[' + ip + '] ' + 'GetIpinfoAPI: No longitude in GetIpinfoAPI response.'
            logging.error(error_message)
            self.longitude = None

        try:  
            self.latitude = float(details.latitude)
        except (AttributeError, TypeError):
            error_message = '[' + ip + '] ' + 'GetIpinfoAPI: No latitude in GetIpinfoAPI response.'
            logging.error(error_message)
            self.latitude = None
    
        # hostname
        try:
            self.hostname = details.hostname
        except AttributeError:
            error_message = '[' + ip + '] ' + 'GetIpinfoAPI: No hostname in GetIpinfoAPI response.'
            logging.error(error_message)
            self.hostname = None

        # AS data
        try:
            asn_name = details.org.split(" ", 1)
            self.as_asn = int(asn_name[0].split('AS')[1])
            try:
                self.as_name = asn_name[1]
            except IndexError:
                error_message = '[' + ip + '] ' + 'GetIpinfoAPI: No as_name in GetIpinfoAPI response.'
                logging.error(error_message)
                self.as_name = None
        except (AttributeError, TypeError):
            error_message = '[' + ip + '] ' + 'GetIpinfoAPI: No as_asn and as_name in GetIpinfoAPI response.'
            logging.error(error_message)
            self.as_asn = None
            self.as_name = None


if __name__ == "__main__":
    pass

   


