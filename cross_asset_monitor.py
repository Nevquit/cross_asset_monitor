from iWAN import iWAN#pip install iWAN
from monitor_msg_tools import dingMsg,sendEmail,genhtml

secretkey = '0ea7cb639be0a1c9bf2073f617bee4be66c7c4d1d0e14853ce3a8410d74a31cb'
Apikey ='1bd59d5aecabc6411a59d5c1daaf3dfde2889627b97d5d5acb05958f4bf9a317'
url = 'wss://apitest.wanchain.org:8443/ws/v3/'
url_main = 'wss://api.wanchain.org:8443/ws/v3/'

class CROSS_ASSET_MONITOR:
    def __init__(self,net,):
        self.net = net
        self.url = {'main':'','test':''}
        self.secretkey = ''
        self.Apikey = ''

        iwan = iWAN.iWAN()