from iWAN import iWAN #pip install iWAN
from monitor_msg_tools import dingMsg,sendEmail,genhtml
import json
import requests
from iWAN_Request import iWAN_Request
from pubkey2address import Gpk2BtcAddr,Gpk2DotAddr,Gpk2XrpAddr #pip install pubkey2address

class CROSS_ASSET_MONITOR:
    def __init__(self,net):
        '''
        :param net: 'main'/'test'
        '''
        self.net = net
        with open('/.iWAN_config','r') as f:
            config = json.load(f)
        self.iwan = iWAN.iWAN(config["url_{}".format(net)],config['secretkey'],config['Apikey'])
        self.dingApi = config["dingApi"]
        self.address = config["emailAddress"]
        self.assetblackList = config['assetblackList']
        self.toBlackList = []
        self.chainInfo = requests.get('https://raw.githubusercontent.com/Nevquit/configW/main/chainInfos.json').json()
        self.poolTokenInfo = requests.get("https://raw.githubusercontent.com/Nevquit/configW/main/crossPoolTokenInfo.json").json()
        def _getChainInfos():
            '''
            parse chainInfo to output chainIDdit,chainAbbr,noEVMChains,evmCrossSC
            :return:
            '''
            chainIDdit ={}
            chainAbbr = {}
            noEVMChains = []
            evmCrossSC = {}
            for chainID in  self.chainInfo[self.net].keys():
                chainName = self.chainInfo[self.net][chainID]["chainName"]
                chainType = self.chainInfo[self.net][chainID]["chainType"]
                evm = self.chainInfo[self.net][chainID]["evm"]
                chainIDdit[chainID] =chainName
                chainAbbr[chainName] = chainType
                if not evm:
                    noEVMChains.append(chainType)
                else:
                    evmCrossSC[chainType] = self.chainInfo[self.net][chainID]['crossScAddr']
            return chainIDdit,chainAbbr,noEVMChains,evmCrossSC
        self.chainIDdit, self.chainAbbr, self.noEVMChains ,self.evmCrossSC= _getChainInfos()
        def _getPoolTokenInfo():
            '''
            parse poolTokenInfo to output poolToken related info
            :return:
            '''
            poolTokenAddr = {}
            fixAmount = {}
            poolTokenList = [int(i) for i in list(self.poolTokenInfo[self.net].keys())]
            for tokenPairID in poolTokenList:
                poolTokenAddr[self.poolTokenInfo[self.net][str(tokenPairID)]['Asset']] = self.poolTokenInfo[self.net][str(tokenPairID)]['TokenAddress']
                fixAmount[self.poolTokenInfo[self.net][str(tokenPairID)]['Asset']] = self.poolTokenInfo[self.net][str(tokenPairID)]['originalAmount']
            return poolTokenAddr, fixAmount, poolTokenList
        self.poolTokenAddr, self.fixAmount, self.poolTokenList = _getPoolTokenInfo()

    def getTokenPairs(self):
        '''
        :return:
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": [
                    {
                        "id": "1",
                        "fromChainID": "2147483708",
                        "fromAccount": "0x0000000000000000000000000000000000000000",
                        "toChainID": "2153201998",
                        "toAccount": "0xe3ae74d1518a76715ab4c7bedf1af73893cd435a",
                        "ancestorSymbol": "ETH",
                        "ancestorDecimals": "18",
                        "ancestorAccount": "0x0000000000000000000000000000000000000000",
                        "ancestorName": "ethereum",
                        "ancestorChainID": "2147483708",
                        "name": "wanETH@wanchain",
                        "symbol": "wanETH",
                        "decimals": "18"
                    }
                ]
            }
        '''
        tokenPairs = self.iwan.sendRequest(iWAN_Request.getAllTokenPairs())
        return tokenPairs
    def getLockedAccount(self,grInfo):
        BTCAddr = Gpk2BtcAddr.GPK2BTCADDRESS(grInfo,net=self.net)
        btcAddress = BTCAddr.Public_key_to_address('BTC')
        ltcAddress = BTCAddr.Public_key_to_address('LTC')
        dogeAddress = BTCAddr.Public_key_to_address('DOGE')
        xrpAddress = Gpk2XrpAddr.GPK2XRPADDRESS().getSmXrpAddr(grInfo)
        dotAddress = Gpk2DotAddr.GPK2DOTADDRESS().getSmDotAddr(grInfo,self.net)
        noEVMLockedAccout = {'LTC':ltcAddress,'XRP':xrpAddress,'BTC':btcAddress,'DOGE':dogeAddress,'DOT':dotAddress}
        return self.evmCrossSC.update(noEVMLockedAccout)


