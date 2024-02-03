# Author: Nike Liu
from datetime import datetime
from DataEngine import DataEngine
from setting.symbols import class_symbols,index_symbols
from event.eventEngine import Event
from event.eventType import *
import time
from PyQt5.QtCore import QTimer,QObject,pyqtSignal
from PyQt5.QtWidgets import QWidget
from setting.account import Account
import pandas as pd
from login import LoginForm
from util.logger import QuantLogger
from util.stock_util import is_trading_day

class MainEngine(QObject):
    """主引擎"""
    logSignal = pyqtSignal(str)
    tickSignal = pyqtSignal(dict)

    def __init__(self, eventEngine):
        super(MainEngine,self).__init__()

        # 记录今日日期
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.saveDataStatus = False
        self.loginStatus = False
        self.timerStatus = False
        self.is_trading_day = is_trading_day()

        # 创建事件引擎
        self.eventEngine = eventEngine
        self.eventEngine.Start()

        # 创建数据引擎
        self.dataEngine = DataEngine()
        self.initData()

        # 注册"登录"的函数
        self.registerHandler(type_=EVENT_LOGIN,handler=self.loginEvent)

        # 注册'更新持仓信息'的函数
        self.registerHandler(type_=EVENT_ACCOUNT, handler=self.upatePositionData)

        # 间歇check的timer
        self.checkTimer()

        # 登录信号绑定动作
        # self.loginSignal.connect(self.createQtimer)
        self.TWindow = QWidget()

        # self.logger = QuantLogger(mainEngine=self,name='main')

    def initData(self):

        # 持仓symbol
        self.mySymbols = self.qryMysymbols()

        # 当日卖出个股
        sql_history = "select code,数量,卖出价,account from 历史单 where 卖出日期 = #" + self.today + "# "
        df_history = self.qryDB(sql_history)

        self.sellSymbols = list(set(df_history['code'].tolist()))

        # 跟踪的个股或者指数
        self.Tracking = list(set(class_symbols + index_symbols + self.sellSymbols))
        # 需要订阅的symbols
        self.subcribeSymbols = list(set(self.Tracking + self.mySymbols))

        if len(self.sellSymbols):
            pre_close_data = self.getTick(self.sellSymbols)[['code', 'pre_close']]
        else:
            pre_close_data = self.getTick(['601318'])[['code', 'pre_close']]

        # 获取持仓DF
        self.dbdata = self.qryPosition(accountName='all')

        # 获取数据中的账户基本信息DF
        self.df_acc = self.dataEngine.qryAccount()
        self.df_acc = self.df_acc.set_index('account')/10000

    def upatePositionData(self,event):
        """trade后更新持仓股和订阅list"""
        self.initData()
        self.pushData()

    def pushData(self):
        """发送tick event"""
        try:
            # 获取tick数据
            tickData = self.getTick(self.subcribeSymbols)
            if tickData is not None:
                # 带有tick数据的持仓个股dataframe
                df_db = self.processData(self.dbdata, tickData)
                if not df_db.empty:
                    # 分帐号汇总
                    df_summary = df_db[['value', 'profit', 'profit_day', 'account']].groupby('account').sum()/10000
                    df_summary = pd.merge(df_summary, self.df_acc, on='account',sort=False)

                    df_summary['code'] = df_summary.index
                    df_summary.rename(columns={'profit_x':'profit', 'cash':'price'}, inplace=True)
                    df_summary['change_rate'] = round(df_summary['profit_day'] / (df_summary['value']-df_summary['profit_day']) * 100, 1)
                    df_summary['profit_rate'] = round(df_summary['profit'] / (df_summary['value']-df_summary['profit']) * 100, 1)
                    df_summary['position'] = round(df_summary['value'] / (df_summary['value']+df_summary['price']) * 100, 1).apply(str) + "%"

                    df_summary['name'] = '汇总'
                    df_summary['qty'] = df_db[['account','qty']].groupby('account').count()
                    df_summary['qty'] = '计数: ' + df_summary['qty'].apply(str)

                    # print(self.df_sum)
                    df_summary[['value', 'profit', 'profit_day', 'price', 'cost']] = round(
                        df_summary[['value', 'profit', 'profit_day', 'price', 'cost']], 2)

                    # 以账号为索引改为自然数，同时保留账号到列中
                    df_summary = df_summary.reset_index(drop=False)
                    self.df_sum = df_summary
                    # 把以下三列改为W为单位
                    df_db[['value', 'profit', 'profit_day']] = round(df_db[['value', 'profit', 'profit_day']]/10000,2)
                    df_db = df_db.append(df_summary,ignore_index=True,sort=False)

                    # 生成板块和指数的tick data，并保存在event字典中。
                    df_tracing = tickData[tickData['code'].isin(self.Tracking)]
                    df_tracing = df_tracing[['code', 'name', 'price', 'change_rate', 'time']].sort_values(by='change_rate',
                                                                                                          ascending=False)
                    # 持仓字典
                    event_tick = {}
                    event_tick['hold_data'] = df_db
                    # 跟踪个股字典,包括当日有卖出的个股
                    event_tick['tracing'] = df_tracing
                    # right_now = time.strftime("%H:%M %S")
                    # 发送订阅的数据
                    self.sendEvent(type_=EVENT_TIMER,event_dict=event_tick)
                    self.tickSignal.emit(event_tick)
                    # print('%s send data2' % right_now)

        except Exception as e:
            print('send data %s' % str(e))

    def createQtimer(self):
        """利用计时器，定时刷新行情"""
        # print(con)
        if self.loginStatus:  # 检查是否登录
            self.refreshNum = 0
            self.logSend('开始更新数据...')
            self.pushData()
            self.timerStatus = True
            # 建立一个计时器
            self.timer = QTimer()
            self.timer.timeout.connect(self.pushData)

            # 设置间隔时间大小ms
            self.timer.start(5000)
        else:
            # 没有登录，则显示登录窗口
            self.login = LoginForm(self)
            self.login.show()

    def intervalCheck(self):
        """间歇检查的项目"""
        right_now = int(time.strftime("%H%M%S"))
        if right_now < 91500:
            self.timer_stop()

        elif right_now > 150010:
            self.timer_stop()
            # 本日为交易日且未保存数据
            if self.is_trading_day and not self.saveDataStatus:
                self.saveData()
        else:
            if self.timerStatus:
                # 检查当日是否为假日
                if not self.is_trading_day:
                    self.timer_stop()
                    self.logSend('休息日，数据停止更新!')
                    # QMessageBox.about(self.TWindow,"提示", "休息日，数据停止更新！")

    def checkTimer(self):
        """另外一个timer检查当前时间是否为交易时间"""
        self.Newtimer = QTimer()
        self.Newtimer.timeout.connect(self.intervalCheck)
        # 每分钟运行一次
        self.Newtimer.start(10000)

    def timer_stop(self):
        if self.timerStatus:
            self.timer.stop()
            self.logSend('停止更新')
            self.timerStatus = False

    def saveData(self):
        """把当日收盘数据保存到db中"""
        if not self.saveDataStatus and self.loginStatus:
            # 先获取db数据
            qry_sql = "select * from 每日净值 where 日期 = #" + self.today + "#"
            qry_re = self.qryDB(qry_sql)
            # 判断是否已经存在当日数据
            if qry_re.empty:
                for account in Account.keys():
                    # 获取该账户下的持仓code
                    dbData = self.df_sum.set_index('account').loc[account]
                    cash = round(dbData['price']*10000,1)
                    stock_value = round(dbData['value']*10000,1)
                    total_value = round((stock_value + cash ), 1)
                    save_sql = "INSERT INTO 每日净值(日期,账户,市值,总资产) VALUES ('" + self.today + "','" + account + "'," \
                             " '" + str(stock_value) + "', '" + str(total_value) + "')"
                    self.excuteSQL(save_sql)
                # 判断是否是第一次保存数据

                # QMessageBox.about(self.TWindow,"提示", "收盘数据已保存！")
                self.logSend('收盘数据已保存！')
            else:
                self.logSend('无需保存，今日数据保存过了！')
            self.saveDataStatus = True

    def qryDB(self,sql,columns = None):
        # 数据库查询
        return self.dataEngine.dbQurey(sql,columns)

    def excuteSQL(self,sql):
        """执行SQL到access"""
        self.dataEngine.excuteSQL(sql)

    def qryPosition(self,accountName):
        """获取持仓dataframe"""
        return self.dataEngine.qryPosition(accountName)

    def qryMysymbols(self,account='all'):
        """ 获取全部持仓的code list"""
        return self.dataEngine.qryMysymbols(account)

    def getAccDict(self):
        """获取账户信息Dict"""
        return self.dataEngine.getAccDict()

    def getTick(self, symbols):
        return self.dataEngine.getTick(symbols)

    # 合并两个dataframe，获取需要的样式
    def processData(self, left, right):
        return self.dataEngine.processData(left,right)

    # 注册事件源，put tick data 到 event
    def sendEvent(self,type_,event_dict):
        event = Event(type_=type_)
        event.dict = event_dict
        self.eventEngine.SendEvent(event)

    # 注册监听函数（数据使用者）
    def registerHandler(self,type_,handler):
        self.eventEngine.AddEventListener(type_, handler)

    def exit(self):
        """退出程序前调用，保证正常退出"""

        # 停止事件引擎
        self.eventEngine.Stop()

        # 保存数据引擎里的合约数据到硬盘
        # self.dataEngine.saveContracts()

    def tradeEvent(self,trade_dict):
        """发送交易事件"""
        self.sendEvent(type_=EVENT_ACCOUNT, event_dict=trade_dict)
        self.logSend('交易成功 %s' % trade_dict)

    def loginEvent(self):
        """登录事件"""
        self.loginStatus = True
        self.logSend('登录成功')
        # 这里不能直接创建timer，因为不允许在子线程中创建。需要利用pyqt的signal发射机制处理。
        # self.loginSignal.emit("用户登录成功")
        self.createQtimer()

    def logSend(self,message):
        right_now = time.strftime("%H:%M %S")
        self.logSignal.emit('%s %s' % (right_now,message))

if __name__ == '__main__':
    from event.eventEngine import EventManager
    ee = EventManager()
    run = MainEngine(ee)
    print(run.positionDict)