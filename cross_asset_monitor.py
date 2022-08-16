from monitor_msg_tools import dingMsg,sendEmail,genhtml
import json
import copy
from monitor_utility import BalanceUtility,StoremanUtility,TokenPairsUtility
import time
class CROSS_ASSET_MONITOR:
    def __init__(self,net):
        '''
        :param net: 'main'/'test'
        '''
        self.net = net
        with open('.iWAN_config.json','r') as f:
            config = json.load(f)
        self.dingApi = config["dingApi"]
        self.address = config["emailAddress"]


def main():
    print('start',time.time())
    #.global variables
    assetblackList = []
    net = 'main'
    iWAN_config = '.iWAN_config.json'
    stm_utl = StoremanUtility.StoremanUtility(net,iWAN_config)
    tlpair_utl= TokenPairsUtility.TokenPairsUtility(net,iWAN_config)
    bal_utl = BalanceUtility.BalanceUtility(net, iWAN_config)
    pooltoken_info,poolTokenIDList = tlpair_utl.getPoolTokenDict()
    btcNodes = {'url':'http://nodes.wandevs.org:26893','user':'wanglu','pwd':'Wanchain888'}
    ltcNodes = {'url':'http://nodes.wandevs.org:26894','user':'wanglu','pwd':'Wanchain888'}
    dogeNodes = {'url':'http://44.239.180.2:26895','user':'wanglu','pwd':'Wanchain888'}

    get_balance = \
        {'BTC': {'method': bal_utl.getBTCsBalance,
                 'parametes': {'chain': 'BTC', 'node': btcNodes['url'], 'user': btcNodes['user'],
                               'password': btcNodes['pwd'], 'address': ''}},  # chain,node,user,password,address
         'LTC': {'method': bal_utl.getBTCsBalance,
                 'parametes': {'chain': 'LTC', 'node': ltcNodes['url'], 'user': ltcNodes['user'],
                               'password': ltcNodes['pwd'], 'address': ''}},
         'DOGE': {'method': bal_utl.getBTCsBalance,
                  'parametes': {'chain': 'DOGE', 'node': dogeNodes['url'], 'user': dogeNodes['user'],
                                'password': dogeNodes['pwd']}},
         'XRP': {'method': bal_utl.getXRPBalance,
                 'parametes': {'nodes': ['wss://nodes.wandevs.org/xrp:443'], 'address': ''}},
         'DOT': {'method': bal_utl.getDOTBalance,
                 'parametes': {'nodes': ['wss://nodes.wandevs.org/polkadot'], 'address': ''}}
         }



    #1. prepare locked accounts to be checked:
    working_groupIds = stm_utl.getWorkingGroupsIds()
    LockedAccs_allGroups = tlpair_utl.getLockedAccountForMultiGrps(working_groupIds)

    #2. get assets information to be checked
    assetCCDit, supportChains = tlpair_utl.getassetCCDit()

    #3. init the report data
    cr_mnt_report = {}
    report_titles = copy.deepcopy(supportChains)
    report_titles.insert(0,'Total_locked_amount_h')
    report_titles.insert(0, 'LockedAmount_Details')
    report_titles.insert(0, 'OriginalChains')
    report_titles.insert(0, 'Asset')
    report_titles.append('MintedTokenAmount')
    report_titles.append('Gap')
    report_titles.append('Status')
    for key in report_titles:
        cr_mnt_report[key] = []

    #4. get locked account balance and mapped tokens
    for asset, assetInfos in assetCCDit.items():
        cr_mnt_report['Asset'].append(asset) #save to report data
        original_chains = list(assetInfos['OriginalChains'].keys())
        original_pool_chain = []
        total_locked_amount_h = 0
        locked_amount_details_h = []
        total_minted_token_amount_h = 0
        total_pool_pre_minted_amount_h = 0
        total_pool_remaining_amount_h = 0
        for originalchain in original_chains: #get locked amount in different original chains then summarize
            chainType = assetInfos['OriginalChains'][originalchain]['chainType']
            assetType = assetInfos['OriginalChains'][originalchain]['assetType']
            ccType = assetInfos['OriginalChains'][originalchain]['ccType']
            locked_amount = 0
            tokenAddr = assetInfos['OriginalChains'][originalchain]['TokenAddr']
            ancestorDecimals = assetInfos['OriginalChains'][originalchain]['ancestorDecimals']
            if assetType == 'coin_noEvm':
                for acc in LockedAccs_allGroups[chainType]:
                    get_balance_method = get_balance[chainType]['method']
                    get_balance_parameters =  get_balance[chainType]['parametes']
                    get_balance_parameters['address'] = acc
                    balance = get_balance_method(**get_balance_parameters)
                    if balance:
                        locked_amount += float(balance)
                    else:
                        print('get {} locked amount failed'.format(asset))
            if assetType == 'coin_evm':
                for acc in LockedAccs_allGroups[chainType]:
                    balance = bal_utl.getEVMChainCoinBalanceViaIwan(acc,chainType)['result']
                    if balance:
                        locked_amount += float(balance)
                    else:
                        print('get {} locked amount failed'.format(asset))
            if assetType == 'token_evm':
                for acc in LockedAccs_allGroups[chainType]:
                    balance = bal_utl.getEVMChainTokenBalanceViaIwan(chainType,acc,tokenAddr)['result']
                    if balance:
                        locked_amount += float(balance)
                    else:
                        print('get {} locked amount failed'.format(asset))
            if ccType == 'pool':
                PoolScAddress = pooltoken_info[asset][chainType]['PoolScAddress']
                pool_remaining_amount = bal_utl.getEVMChainTokenBalanceViaIwan(chainType,PoolScAddress,tokenAddr)['result']
                pool_remaining_amount_h = float(int(pool_remaining_amount)/(1*10**int(ancestorDecimals)))
                total_pool_remaining_amount_h += pool_remaining_amount_h
                total_pool_pre_minted_amount_h += float(pooltoken_info[asset][chainType]['originalAmount'])
                cr_mnt_report[originalchain].append("Pool_remaining_amount: {}".format(pool_remaining_amount_h)) #pool preminted token is recored to report data as mapped token
                original_pool_chain.append(originalchain)

            locked_amount_h = float(locked_amount/(1*10**int(ancestorDecimals)))
            locked_amount_details_h.append(str(locked_amount_h))
            total_locked_amount_h +=locked_amount_h

        #get the not supported chains
        notSupportedChains = set(supportChains) - set(assetInfos['MapChain'].keys()) - set(original_pool_chain)
        for map_chain, map_tokenInfo in assetInfos['MapChain'].items(): #get minted amount in different mapped chains then summarize
            tokenAddr = map_tokenInfo['TokenAddr']
            chainType = assetInfos['MapChain'][map_chain]['chainType']
            map_amount = int(bal_utl.getMapToeknTotalSupply(chainType, tokenAddr)['result'])  # wei unit
            map_amount_h = float(map_amount / (1 * 10 ** int(map_tokenInfo['decimals'])))
            total_minted_token_amount_h += map_amount_h
            cr_mnt_report[map_chain].append(map_amount_h) #recored to report data

        cr_mnt_report['OriginalChains'].append('\n'.join(original_chains)) #save to report data
        cr_mnt_report['LockedAmount_Details'].append('\n'.join(locked_amount_details_h)) #save to report data
        cr_mnt_report['Total_locked_amount_h'].append(str(total_locked_amount_h)) #save to report data
        cr_mnt_report['MintedTokenAmount'].append(str(total_minted_token_amount_h))
        for notSupportedChain in notSupportedChains:
            cr_mnt_report[notSupportedChain].append('//')

        #5 assert data
        gap = (total_locked_amount_h + total_pool_remaining_amount_h) - total_minted_token_amount_h-total_pool_pre_minted_amount_h
        if gap >= -0.00000001:  # 0,consider the precision use -0.0000000001 instead of 0
            status = 'Pass'
        else:
            status = 'Alert-{} locked amount is less than minted amount {}'.format(asset, -gap)
        cr_mnt_report['Status'].append(status)
        cr_mnt_report['Gap'].append(gap)

        #6.
        html = genhtml.html_build(cr_mnt_report,'Cross_Chain_Asset')
        with open('./report','w') as f:
            f.write(html)
    print('stop', time.time())
    print(json.dumps(cr_mnt_report))


if __name__ == '__main__':
    main()
