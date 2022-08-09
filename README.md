# cross_asset_monitor
  1. need to add 'iWAN_config.json' under cross_asset_monitor folder
        {
            "secretkey": "your secretkey", 
            "Apikey": "your apikey",
            "url_test": "wss://apitest.wanchain.org:8443/ws/v3/",
            "url_main": "wss://api.wanchain.org:8443/ws/v3/",
            "dingApi":"https://oapi.dingtalk.com/robot/send?access_token=your ding robot token",
            "emailAddress":"your email address",
            "assetblackList":[black asset list]
        }
  2. when add the no evm chain, need update cross_asset_monitor.getLockedAccount function to suuport the related chains.
  3. when add the evm chain, just need to update 'https://github.com/Nevquit/configW/blob/main/chainInfos.json'
  