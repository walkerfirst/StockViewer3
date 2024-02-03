# Author: Nike Liu
# import tushare as ts
import time
from util.database import conn
from urllib import request,error
import pandas as pd
from datetime import datetime
from setting.account import Account


class DataEngineTS(object):
    """从tushare获取tick数据数据，df是一个含有'code'列名的打他frame，symbol是一个list，则返回多条数据（dataframe）"""
    def __init__(self,symbolArry):
        self.symbolArray = symbolArry
        try:
            # time.sleep(1)
            L = int(len(self.symbolArray)/2)
            self.ts_df = ts.get_realtime_quotes(self.symbolArray[:L])
            self.ts_df2 = ts.get_realtime_quotes(self.symbolArray[L:])
            self.ts_df = self.ts_df.append(self.ts_df2)
            self.ts_df[['pre_close', 'price']] = self.ts_df[['pre_close', 'price']].astype(float)

        except Exception as e:
            print('TS 获取数据出现异常: %s,%s' % (str(datetime.now()),str(e)))
            # self.ts_df = ts.get_realtime_quotes(self.symbolArray)

        # 判断获取的数据是否补全，若是，则重新获取
        if self.ts_df.empty:
            # time.sleep(1)
            print('本次返回数据为空')
            self.ts_df = ts.get_realtime_quotes(self.symbolArray)
        # 处理停牌的股票
        for index in self.ts_df.index:
            item = self.ts_df.iloc[index]['price']
            if item == 0.0:
                self.ts_df.loc[index,'price'] = self.ts_df.iloc[index]['pre_close']
                time.sleep(0.05)

        self.ts_df = self.ts_df[['code', 'name', 'pre_close', 'price','time']]
        self.ts_df['change_rate'] = round((self.ts_df['price'] / self.ts_df['pre_close'] - 1) * 100, 2) # 当日变化
        self.ts_df = self.ts_df[['code', 'name', 'price','pre_close','change_rate','time']]

class DataEngineSina(object):
    """从新浪网爬虫数据，list后面可以跟一个列表，则返回多条数据"""

    def __init__(self,symbolArry):
        self.symbolArray = symbolArry
        self.data = self.getStockData()

    def __request(self, symbol):
        url = "http://hq.sinajs.cn/?list=%s" % symbol
        # 通过浏览器伪装爬取数据：
        headers = ("referer","https://finance.sina.com.cn")  # 这里模拟浏览器 ,添加referer后不再显示 Kinsoku jikou desu!
        # 原来的 headers   'User-Agent'," Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"" Chrome/66.0.3359.139 Safari/537.36",
        opener = request.build_opener()
        opener.addheaders = [headers]
        request.install_opener(opener)

        try:
            return request.urlopen(url, data=None, timeout=5).read().decode('gbk')
        except error.URLError as e:
            print('Sina 获取数据出现异常: %s,%s' % (str(datetime.now()),str(e)))
            # time.sleep(2)
            # return request.urlopen(url, data=None, timeout=8).read().decode('gbk')


    def processSymbol(self):
        """处理list，得到一个符合新浪代码标准的字符串"""
        self.symbolString = ""
        # print(self.symbolArray,type(self.symbolArray))
        for symbol in self.symbolArray:
            # 去除首尾指定的字符
            symbol = symbol.strip()

            # 上证 股票以6开头，基金以5开头，B股以9开头
            if len(symbol) == 0:
                return
            if symbol[0] == '6' or symbol[0] == '5' or symbol[0] == '9':
                symbol = "sh" + symbol
            # 深证 股票以3，0开头，基金以1开头, B股以2开头
            if symbol[0] == '3' or symbol[0] == '0' or symbol[0] == '1' or symbol[0] == '2':
                symbol = "sz" + symbol

            if len(self.symbolString) > 0:
                self.symbolString = self.symbolString + "," + symbol
            else:
                self.symbolString = symbol
            # 获取N条交易数据，返回列表
        # print(self.symbolString)

    def getStockData(self):
        self.processSymbol()

        request_data = self.__request(self.symbolString)
        if "FAILED" in request_data:
            request_data = self.__request(self.symbolString)
        dataArray = request_data.split(';')
        new_list = []
        for textPiece in dataArray:
            data = textPiece.split(',')
            # print(data)
            if len(data) == 1:
                continue
            name = data[0].split('\"')[1]
            code = data[0].split('_')[2].split('=')[0][2:]
            price = float(data[6])
            pre_close = float(data[2])
            if code[:3] == '399':
                price = float(data[3])
            time = data[-2]
            date = data[-3]
            if code[0] == '6' or code[0] == '5' or code[0] == '9':
                time = data[-3]
                date = data[-4]
            # 判断如果是指数，则取整数
            if price > 1500:
                price = int(price)
                pre_close = int(pre_close)
            # 针对刚上市还没有价格的debug
            if pre_close == 0:
                pre_close = 10
            # 针对停牌或者不开盘的时间的处理
            if price <= 0:
                price = pre_close
            changeNum = round((price/ pre_close- 1.0) * 100,2)
            list = [code,name,price,pre_close,changeNum,date,time]
            new_list.append(list)
        df = pd.DataFrame(new_list,columns=['code','name','price','pre_close','change_rate','date','time'])
        return df


class DataEngine(object):
    """获取数据的类"""
    def __init__(self):

        # 持仓账户
        self.account = Account.keys()

        # 保存合约详细信息的字典
        self.positionDict = {}
        # 更新持仓字典
        self.getPostionDict()

        # 持仓code list
        self.mySymbols = []
        self.qryMysymbols()

        # 账户基本信息
        self.accDict = {}
        # 更新账户字典
        self.getAccDict()

    # db 查询
    def dbQurey(self,sql,columns=None):
        """读取access，将sql转成 转成df, column_list 为 df 的列名"""
        df = pd.read_sql(sql, conn)
        if columns is not None:
            df.columns = columns
        # 得到持仓dataframe
        return df

    # db 写入
    def dbSave(self,df,dbname):
        """df写入access，dbname为table名称"""
        df.to_sql(name=dbname, con=conn,if_exists='append')
        return

    def excuteSQL(self,sql):
        """执行SQL到access"""
        cursor = conn.cursor()
        cursor.execute(sql)
        cursor.commit()

    def qryPosition(self,accountName = 'all'):
        """取持仓账户的dataframe数据，默认为全部获取"""
        _columns = ['code', 'qty', 'cost','account']
        # print(columns)
        # 得到持仓dataframe
        if accountName == 'all':

            sql = "SELECT code,数量合计,平均成本,account FROM 持仓概览"

        else:
            sql = "SELECT code,数量合计,平均成本,account FROM 持仓概览 where account='" + accountName + "'"
        data = self.dbQurey(sql, _columns)
        return data

    def qryAccount(self,accountName = 'all'):
        """获取账户的基本信息dataframe数据，默认为全部获取"""

        _columns = ['account','cash', 'cost','profit']
        # print(columns)
        # 得到持仓dataframe
        if accountName == 'all':
            _sql = "SELECT code,cash,投入本金,实现盈利  FROM 账户"
        else:
            _sql = "SELECT code,cash,投入本金,实现盈利 FROM 账户 where code= '" + accountName + "'"
        _data = self.dbQurey(_sql, _columns)
        return _data


    def qryMysymbols(self,name='all'):
        """ 取全部持仓的code list"""
        # self.qryPosition()
        # print(self.positionDict['all'])
        self.mySymbols = self.qryPosition(accountName='all')['code'].tolist()
        # 去重
        self.mySymbols = list(set(self.mySymbols))
        return self.mySymbols

    def getPostionDict(self):
        """将持仓信息df添加到字典中"""
        self._df = self.qryPosition(accountName='all')
        for name in self.account:
            self.positionDict[name] = self._df[self._df['account'] == name]
        self.positionDict['all'] = self._df

    def getAccDict(self):
        """账户基本信息汇总后，将series添加到Dict中"""
        accdb = self.qryAccount(accountName='all')
        for name in self.account:
            self.accDict[name] = accdb[accdb['account'] == name].sum()
        accdb_all = accdb.sum()
        # 重置series的 name值
        accdb_all['code'] = 'all'
        self.accDict['all'] = accdb_all
        return self.accDict

    def getTick(self,symbols):
        """获取实时的tick数据"""
        try:
            # 从sina网页爬取
            # print(symbols)
            self._data = DataEngineSina(symbols).getStockData()
            # self._data = DataEngineTS(symbols).ts_df

            return self._data

        except Exception as e:
            print('getTick 出现异常: %s,%s' % (str(datetime.now()),str(e)))
            return None
            # 从tushare获取
            # self._data = DataEngineSina(symbols).getStockData()
            # self._data = DataEngineTS(symbols).ts_df
            # self._data = pd.DataFrame()  # 若错误，则返回一个空df
        # print('self.data=',self._data)


    # 订阅需要推送的tick 列表
    def subcribeTick(self,symbols):
        """未完成"""
        for symbol in symbols:
            self.subcribeSymbols.append(symbol)

    def processData(self,left,right):
        """处理两个df，得到持仓股票需要数据格式"""
        self.df = pd.merge(left, right, on='code',sort=False)
        self.df['profit_rate'] = round((self.df['price'] / self.df['cost'] - 1) * 100, 1)  # 利润率
        self.df['qty'] = self.df['qty'].astype('int')
        self.df['value'] = self.df['price'] * self.df['qty'] # 市值
        self.total_value = self.df['value'].sum()
        self.df['position'] = round(self.df['value'] / self.total_value * 100, 1)
        self.df['profit'] = (self.df['price'] - self.df['cost']) * self.df['qty']
        self.df['profit_day'] = (self.df['price'] - self.df['pre_close']) * self.df['qty']
        self.df = self.df.sort_values(by='change_rate', ascending=False)
        # [['code', 'name', 'qty','position', 'cost', 'price', 'value', 'profit_day', 'change_rate', 'profit',
        # 'profit_rate', 'pre_close', 'time']]
        return self.df
        

if __name__ == '__main__':

    symbol = ['159915','002624']
    win = DataEngine()
    data = win.qryAccount(accountName='all')
    # data = data[data['code'].isin(symbol)]
    print(data)
    win.dbSave(data,'test')