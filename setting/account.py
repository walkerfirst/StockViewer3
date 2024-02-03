# Author: Nike Liu

Account =  {"HX_L":{"name":"华鑫",
           "SZ": 197963622,
           "SH": "A456100201",
           "cost": 400000,
            "fei": 0.0003,
            "fei_etf" : 0.0003,
            "min_fei":5
      },
      "HT_L":{"name":"华泰",
           "SZ": 134172366,
           "SH": "A213805806",
           "cost": 0,
            "fei": 0.00018,
            "fei_etf": 0.0001,
            "min_fei": 5
      },
       "GL_J":{"name":"国联蒋",
           "SZ": 288050399,
           "SH": "A756345059",
           "cost": 285000,
            "fei": 0.0002,
            "fei_etf": 0.0001,
            "min_fei": 5
      },
        "ZH_F": {"name": "中航福",
                 "SZ": 2176073453333333333,
                 "SH": 'A685769513xxxx',
                 "cost": 15000,
                 "fei": 0.0001,
                 "fei_etf": 0.00006,
                 "min_fei": 0.01
                 }
             }

account_position ={197963622:'HX_L',
                   'A456100201': 'HX_L',
                   "A756345059":'GL_J',
                   288050399:'GL_J',
                   217607345:'GF_L',
                   'A685769513':'GF_L',
                   134172366:'HT_L',
                   'A213805806': 'HT_L'}


Account_drop = {
     "GF_L":{"name":"GF_L",
           "SZ": 217607345,
           "SH": 'A685769513',
           "cost":179500,
             "fei": 0.0001,
             "fei_etf": 0.00006,
             "min_fei": 0.01
           }}
if __name__ == '__main__':
      # 通过字典的值查询key
      for key in Account.keys():
          new = Account[key]
          for index in account_position.keys():
              if index in list(new.values()):
                  print(key)
