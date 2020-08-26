import requests
import ipaddress

from apis import GetIpinfoAPI, GetBGPViewAPI

STATUS_OK = 0
STATUS_FAIL = -1
ERROR_BAD_REQUEST = -1
ERROR_NO_DATA = -2


def make_request(url, params=None):
    try: 
        if params == None:
            resp = requests.get(url=url)
        else:
            resp = requests.get(url=url, params=params)
    except:
        return ERROR_BAD_REQUEST

    data = resp.json()

    if data['status'] != 'ok':
        return ERROR_BAD_REQUEST
    else:
        return data


def get_rir_for_ip(ip) -> str:
    '''
    This data call shows which RIR(s) allocated/assigned a resource.
    '''
    url = 'https://stat.ripe.net/data/rir/data.json'
    params = dict(resource=ip)

    data = make_request(url, params)

    if data in (ERROR_BAD_REQUEST, ERROR_NO_DATA):
        return data
    else:
        rirs = data['data']['rirs']
        if len(rirs) == 0:
            return ERROR_NO_DATA
        else:
            return rirs[0]['rir'].strip()


class AsObject():
    def __init__(self):
        # AS_TABLE (Autonomous system)
        self.as_asn = None # 
        self.as_name = None # 
        self.as_route = None #
        self.as_num_addresses = None 
        self.as_rir = None # 
        self.as_description = None # 
        self.as_prefix_description = None # 
        self.as_abuse_contact_email = None # 
        
class IpObject():
    def __init__(self):
        # IP TABLE
        self.city = None
        self.country_name = None
        self.longitude = None
        self.latitude = None
        self.hostname = None
        self.timestamp_first = None
        self.timestamp_last = None


class IpData(AsObject, IpObject):
    def __init__(self, rir, ip):
        AsObject.__init__(self)
        IpObject.__init__(self)

        self.status = STATUS_FAIL
        self.as_rir = rir
        self.ip = ip

    def get_data(self):
        self._get_BGPViewAPI_data()
        self._get_IpinfoAPI_data()

        # ONLY FOR DEBUG
        # self._print_ip_data()

        #preverimo če smo dobili vse informacije
        if None not in (self.as_asn, self.as_name, self.as_route, self.as_rir, self.ip):
            self.status = STATUS_OK

    def _get_BGPViewAPI_data(self):
        '''
        Get data using BGPViewAPI.
        '''
        api_bgpview = GetBGPViewAPI()
        api_bgpview.get_data(self.ip)
        self.as_asn = api_bgpview.as_asn
        self.as_name = api_bgpview.as_name
        self.as_route = api_bgpview.as_route
        self.as_num_addresses = self._count_ip_addersses(self.as_route)
        self.as_description = api_bgpview.as_description
        self.as_prefix_description = api_bgpview.as_prefix_description
        self.as_abuse_contact_email = api_bgpview.as_abuse_contact_email
        
    def _get_IpinfoAPI_data(self):
        '''
        Get data using IpinfoAPI.
        '''
        api_ipinfo = GetIpinfoAPI()
        api_ipinfo.get_data(self.ip)
        self.city = api_ipinfo.city
        self.country_name = api_ipinfo.country_name
        self.longitude = api_ipinfo.longitude
        self.latitude = api_ipinfo.latitude
        self.hostname = api_ipinfo.hostname

    def _print_ip_data(self):
        print(self.ip)
        print(self.as_rir)
        print(self.as_route)
        print('as_description:', self.as_description)
        print('as_prefix_description', self.as_prefix_description)
        print(self.as_abuse_contact_email)
        print(self.country_name)
        print(self.longitude)
        print(self.latitude)
        print(self.hostname)
        print('as_asn:', self.as_asn)
        print('as_name:', self.as_name)
        print('-----------------------------')

    def _count_ip_addersses(self, subnet):
        try:
            return int(ipaddress.ip_network(subnet, strict=False).num_addresses)
        except:
            error_message = '[' + subnet + '] ' + ' error in _count_ip_addersses'
            logging.error(error_message)
            return None


if __name__ == "__main__":
    pass
