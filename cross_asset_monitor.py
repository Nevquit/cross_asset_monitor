from iWAN import iWAN#pip install iWAN
from monitor_msg_tools import dingMsg,sendEmail,genhtml

class CROSS_ASSET_MONITOR:
    def __init__(self,net,):
        self.net = net
        self.url = {'main':'','test':''}
        self.secretkey = ''
        self.Apikey = ''

        iwan = iWAN.iWAN()