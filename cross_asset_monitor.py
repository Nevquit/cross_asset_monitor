from iWAN import iWAN#pip install iWAN
from monitor_msg_tools import dingMsg,sendEmail,genhtml
import json


class CROSS_ASSET_MONITOR:
    def __init__(self,net,):
        self.net = net
        self.url = {'main':'','test':''}
        with open('/.iWAN_config','r') as f:
            config = json.load(f)
        self.iwan = iWAN.iWAN(config["url_{}".format(net)],config['secretkey'],config['Apikey'])
        self.dingApi = config["dingApi"]
        self.address = config["emailAddress"]
        self.assetblackList = ['EOS']
        self.toBlackList = []
        self.chainInfo = requests.get('https://raw.githubusercontent.com/Nevquit/configW/main/chainInfos.json').json()
        self.poolTokenInfo = requests.get("https://raw.githubusercontent.com/Nevquit/configW/main/crossPoolTokenInfo.json").json()