import sys,re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime,Qt,pyqtSignal
from PyQt5.QtGui import QIcon
from BaseQWidgets import BaseStandardTable2,BaseDFTable
from trading.trading import Trading
from trading.填权处理 import stcokprocess
from trading.资金进出处理 import ZJProcess
import pandas as pd
import math,time
from DataEngine import DataEngine
from event.eventType import *

class Myhold2(BaseStandardTable2):
    # 设置表头
    tableheader = ['代码', '名称','数量', '仓位(%)', '成本', '当前价', '市值', '当日亏损', '涨跌幅(%)', '浮动盈亏', '盈亏(%)']
    dataSignal = pyqtSignal(dict)
    def __init__(self,mainEngine,account):

        super(Myhold2, self).__init__()
        # 初始化引擎
        self.mainEngine = mainEngine
        self.account = account

        # 把 pyqt信号与方法关联
        # self.mainEngine.tickSignal.connect(self.setModels)
        self.dataSignal.connect(self.setModels)
        self.mainEngine.registerHandler(type_=EVENT_TIMER,handler=self.initData)

    def initData(self,event):

        self.data = event.dict
        # print('data')
        self.dataSignal.emit(self.data)

    def setModels(self,data_dict):
        """更新数据到model"""
        # right_now = time.strftime("%H:%M %S")
        # print('%s myhold set model' % right_now)
        try:
            # 持仓动态数据
            self.data2 = data_dict['hold_data']
            if not self.data2.empty:
                # data = data[data['account'] == self.account]
                self.data2 = self.data2.reset_index(drop=True)
                # print(data.head(5))
                # 重新设置选取的列，注意顺序
                self.data2 = self.data2[['code', 'name', 'qty', 'position', 'cost', 'price', 'value', 'profit_day', 'change_rate', 'profit',
                  'profit_rate']]

                # 把数据更新到model中去

                self.update_data_to_model(self.data2)

                # 设置列的字体颜色
                self.setForeground(self.data2,byname='profit_day')
                self.setForeground(self.data2,byname='change_rate')
                self.setForeground(self.data2,byname='profit_rate')
                self.setForeground(self.data2,byname='profit')
                self.setForeground(self.data2,byname='price')
                # print('%s myhold set model' % right_now)
        except Exception as e:
            print('myhold set model 错误 %s' % str(e))

    def showContextMenu(self,pos):
        """创建右键菜单"""
        self.tableView.contextMenu = QMenu(self)
        # self.tableView.contextMenu.popup(QCursor.pos())  # 菜单显示的位置,汇报警告信息
        self.tableView.contextMenu.move(self.mapToGlobal(pos))  # 菜单显示的位置

        row_num = -1
        for i in self.tableView.selectionModel().selection().indexes():
            row_num = i.row()

        try:
            if row_num is not None:
                code = self.model.item(row_num, 0).text()
                name = self.model.item(row_num, 1).text()
                # print(code,name)
                data_buy = [code, name, '买入',self.account]
                data_sell = [code, name, '卖出',self.account]
                # 中签的成本价格的计算

                cost = self.model.item(row_num, 4).text()

                data_ZQ = [code, name, '中签卖出',self.account,cost]
                data_HL = [code, name, '现金红利',self.account,cost]

                actionBuy = self.tableView.contextMenu.addAction('买入')
                actionBuy.triggered.connect(lambda: self.actionHandler(data_buy))

                actionSell = self.tableView.contextMenu.addAction('卖出')
                actionSell.triggered.connect(lambda: self.actionHandler(data_sell))

                actionZQ = self.tableView.contextMenu.addAction('中签卖出')
                actionZQ.triggered.connect(lambda: self.actionHandler(data_ZQ))

                actionHL = self.tableView.contextMenu.addAction('现金红利')
                actionHL.triggered.connect(lambda: self.actionHandler(data_HL))

                actionTQ = self.tableView.contextMenu.addAction('填权处理')
                actionTQ.triggered.connect(lambda: self.stockprocessprice(data_buy))

                actionDetail = self.tableView.contextMenu.addAction('买入明细')
                actionDetail.triggered.connect(lambda: self.showDetails(data_buy))

                actionHistory = self.tableView.contextMenu.addAction('历史明细')
                actionHistory.triggered.connect(lambda: self.showHistory(data_buy))

                actionZJ = self.tableView.contextMenu.addAction('资金进出操作')
                actionZJ.triggered.connect(lambda: self.ZJProcess(data_buy))
                self.tableView.contextMenu.show()
                # self.reflash_db_data()
        except Exception as e:
            print("打开右键菜单错误 %s" %(str(e)))

    def actionHandler(self,option):
        """交易处理对话框"""
        self.dialog_trading = Trading(option,self.mainEngine)
        self.dialog_trading.show()

    def stockprocessprice(self,option):
        """填权处理对话框"""
        self.dialog_stock = stcokprocess(option,self.mainEngine)
        self.dialog_stock.show()

    def ZJProcess(self, option):
        """资金进出处理对话框"""
        self.dialog_ZJ = ZJProcess(option,self.mainEngine)
        self.dialog_ZJ.show()

    def showDetails(self,option):
        """展示买入明细对话框"""
        if "汇总" not in option[1]:
            code = option[0]
            read_sql = "select ID,买入日期,名称,买入价,数量 from buy where 结单 = 'N' AND code = '" + code + "'"
            column_list = ['序号', '日期', '名称', '买入价', '数量']
            buy_history = self.mainEngine.qryDB(read_sql, columns=column_list)
            self.dialog_details = BaseDFTable()
            self.dialog_details.update_model(buy_history)
            self.dialog_details.setWindowTitle("买入明细")
            self.dialog_details.setGeometry(600, 600, 1080, 800)
            self.dialog_details.show()
        else:
            QMessageBox.about(self, "对话框", "汇总没有明细")

    def showHistory(self,option):
        """展示交易明细对话框"""
        name = option[1]
        if "汇总" not in name:
            code = option[0]
            read_sql = "select 卖出日期,数量,买入价,卖出价,盈利,利润率 from 历史单 where code = '" + code + "'"
            column_list = ['日期', '数量', '买入价', '卖出价','盈利','利润率(%)']
            trade_history = self.mainEngine.qryDB(read_sql, columns=column_list)
            if not trade_history.empty:
                # 添加汇总行
                trade_history = addSummary(trade_history)
                trade_history = trade_history[['日期', '数量', '买入价', '卖出价', '盈利', '利润率(%)']]  # 重新列排序
                self.dialog_history = BaseDFTable()
                self.dialog_history.update_model(trade_history)
                self.dialog_history.setWindowTitle(" %s  历史明细" % name)
                self.dialog_history.setGeometry(600, 600, 1080, 800)
                self.dialog_history.show()
            else:
                QMessageBox.about(self, "对话框", "没有记录")
        else:
            QMessageBox.about(self, "对话框", "汇总没有明细")

def addSummary(df):
    """根据历史交易明细生成汇总行"""
    df_sum = pd.Series()  # 新建一个series，其实这里也可新建一个字典。
    df_sum['买入价'] = (df['数量'] * df['买入价']).sum()
    df_sum['卖出价'] = (df['数量'] * df['卖出价']).sum()
    df_sum['盈利'] = df['盈利'].sum()
    df_sum['数量'] = df['数量'].sum()
    if df_sum['买入价'] >0:
        df_sum['利润率(%)'] = df_sum['盈利'] / df_sum['买入价']
        if '名称' in df.columns:
            df_sum['名称'] = '汇总'

        # 将series添加到df的最后一行。
        df = df.append(df_sum, ignore_index=True,sort=False)
        # df.fillna('', inplace=True)
        return df
    else:
        return None

class IndexTable2(BaseStandardTable2):
    # 设置表头
    tableheader = ['代码', '名称', '当前价', '涨跌幅(%)','时间']

    def __init__(self,mainEngine,symbols):
        super(IndexTable2, self).__init__()
        # 初始化引擎
        self.mainEngine = mainEngine
        self.symbols = symbols
        # 连接信号与槽函数
        self.mainEngine.tickSignal.connect(self.setModels)

    def setModels(self,data_dict):
        try:
            data = data_dict['tracing']
            data = data[data['code'].isin(self.symbols)]
            if not data.empty:
                # 重置索引，不然会出错
                data = data.reset_index(drop=True)
                time.sleep(1)
                self.update_data_to_model(data)

                # 设置第几列的字体颜色
                self.setForeground(data,byname='change_rate')
                # right_now = time.strftime("%H:%M %S")
                # print('%s index set model' % right_now)

        except Exception as e:
            print('index set model 错误 %s' % e)

    def showContextMenu(self, pos):
        pass

class StatusForm(QWidget):
    def __init__(self,mainEngine):
        super(StatusForm, self).__init__(flags=Qt.WindowFlags())
        self.mainEngine = mainEngine
        # self.rundata = InitData(self.mainEngine)
        # self.dataSignal = self.rundata.dataSignal
        # 连接信号与槽函数
        # self.dataSignal.connect(self.setModel)
        self.mainEngine.tickSignal.connect(self.setModel)
        self.initUI()

    def initUI(self):

        self.label_time = QLabel('显示当前时间')
        self.label_today = QLabel()
        self.label_float = QLabel()
        self.label_position = QLabel()
        self.label_cash = QLabel()
        self.label_total = QLabel()

        # 建立一个网格布局
        layout = QGridLayout(self)
        # 把label控件添加到网格布局中

        layout.addWidget(self.label_today,0, 1)
        layout.addWidget(self.label_float, 0, 2)
        layout.addWidget(self.label_position, 0, 3)
        layout.addWidget(self.label_cash, 0, 4)
        layout.addWidget(self.label_total, 0, 5)

        # 设置网格内容右对齐
        layout.addWidget(self.label_time, 0, 6,1,2,alignment=Qt.AlignRight)
        # self.MainLayout.addLayout(layout)

        self.setLayout(layout)

    def setModel(self,data_dict):
        # 获取系统现在的时间
        time = QDateTime.currentDateTime()
        # 设置系统时间显示格式
        timeDisplay = time.toString("yyyy-MM-dd hh:mm:ss dddd")
        try:
            # 在标签上显示时间
            self.label_time.setText(timeDisplay)
            data = data_dict['hold_data'][['name','value','profit','profit_day','price','cost']]
            data = data[data['name'] == '汇总']

            self.series = data[['value','profit','profit_day','price','cost']].sum().round(decimals=2)
            cash = self.series['price']
            cost = self.series['cost']

            total_day = self.series['profit_day']
            total_value = self.series['value']
            total_day_rate = round(total_day/(total_value-total_day)*100,1)
            float_profit = self.series['profit']
            total_rate = round(float_profit/(total_value-float_profit)*100,1)
            total_ = round(total_value + cash, 2)
            total_profit = round((total_ - cost),2)

            today_str = "TODAY: " + str(total_day) + " (" + str(total_day_rate) + "%)"
            float_str = "FLOAT: " + str(float_profit) + " (" + str(total_rate) + "%)"
            position_str = "POS: " + str(total_value) + " / (" + str(round(total_value/(total_value + cash)*100,1)) + "%)"
            cash_str = "CASH: " + str(cash)
            total_str = "TOTAL: " + str(total_) + " - " + str(cost) + " = " + str(total_profit) +\
                        " (" + str(round(total_profit/cost*100,1)) + "%)"

            # 设置label的数据
            self.label_today.setText(today_str)
            self.label_float.setText(float_str)
            self.label_position.setText(position_str)
            self.label_cash.setText(cash_str)
            self.label_total.setText(total_str)
        except Exception as e:
            print('Status Form update 错误 %s' % e)

class SearchDB(QWidget):
    def __init__(self,dbname):
        super(SearchDB,self).__init__()
        self.dbname = dbname
        self.initUi()

    def initUi(self):
        self.setWindowTitle("搜索%s窗口" % self.dbname)
        self.setWindowIcon(QIcon('./res/draw.png'))
        layout = QVBoxLayout()
        uplayout = QHBoxLayout()
        self.setGeometry(500, 500, 1580, 1080)  # 窗口坐标和窗口大小
        self.nameLineEdit = QLineEdit("")
        # 下来列表格式
        self.optionBox = QComboBox()
        self.optionBox.addItem('代码',"code")
        self.optionBox.addItem('名称',"名称")
        self.optionBox.addItem('日期YYYY/M/D',"日期")
        self.optionBox.addItem('账户', "account")
        self.confirm_Btn = QPushButton('搜索')
        # layout.setSpacing(10)
        uplayout.addWidget(self.nameLineEdit)
        uplayout.addWidget(self.optionBox)
        uplayout.addWidget(self.confirm_Btn)

        self.confirm_Btn.clicked.connect(self.Addsearch)
        layout.addLayout(uplayout,1)
        self.dataView = BaseDFTable()
        self.RecentSellHistory()
        layout.addWidget(self.dataView, 2)
        self.setLayout(layout)

    def RecentSellHistory(self):
        """显示最近卖出记录"""
        recently_sell_sql = "select top 10 卖出日期,code,名称,数量,买入价,卖出价,盈利,利润率 from 历史单 ORDER BY 卖出日期 DESC"
        column_list = ['日期', '代码', '名称', '数量', '买入价', '卖出价', '盈利', '利润率(%)']
        sell_history = DataEngine().dbQurey(recently_sell_sql, columns=column_list)
        if not sell_history.empty:
            # 添加汇总行
            sell_history = addSummary(sell_history)
            sell_history = sell_history[column_list]  # 重新列排序
            self.dataView.update_model(sell_history)

    def Addsearch(self):

        selected = self.optionBox.itemData(self.optionBox.currentIndex())  # 获取下来框的值
        searchName = self.nameLineEdit.text()
        # 首先处理列名
        if self.dbname == '历史单' and selected == '日期':
            selected = '卖出日期'
        if self.dbname == '研报':
            columns = ['code', '名称', '日期', '期数', '标记', 'account']
        else:
            columns = ['code', '名称', '数量', '买入价', '卖出价', '卖出日期', '盈利', '利润率', 'account']

        read_sql = "select * from " + self.dbname + " where " + selected + " like '%" + searchName + "%'"
        try:
            # 需要展示的数据
            data = DataEngine().dbQurey(read_sql)

            if '利润率' in data.columns:
                # 调整日期显示格式
                data.rename(columns={'利润率': '利润率(%)','卖出日期':'日期'}, inplace=True)
            #     # 添加汇总行
                data = addSummary(data)[['code', '名称', '数量', '买入价', '卖出价', '日期', '盈利', '利润率(%)', 'account']]\
                    .sort_values(by='日期', ascending=False)

            self.dataView.update_model(data)

        except Exception as e:
            print('search DB %s' % e)


class AccountDetails(QWidget):
    def __init__(self,mainEngine):
        self.mainEngine = mainEngine
        # self.mainEngine.logSend('显示账户信息')
        super(AccountDetails, self).__init__()
        # 需要展示的数据
        self.getData()
        layout = QVBoxLayout()
        self.dialog_account = BaseDFTable()
        self.dialog_account.update_model(self.df_account)
        self.dialog_account.setColumnColor('浮动盈亏')
        self.setWindowTitle("账户信息概览")
        self.setGeometry(600, 600, 1080, 550)
        layout.addWidget(self.dialog_account)
        self.setLayout(layout)
        self.show()

    def getData(self):

        self.df_account = self.mainEngine.df_sum[['account', 'cost', 'price', 'value']].sort_values(by='value', ascending=False)
        df_sum = round(self.df_account[['cost', 'price', 'value']].sum(), 2)
        df_sum['account'] = '汇总'
        self.df_account = self.df_account.append(df_sum, ignore_index=True, sort=False)
        self.df_account['total'] = round(self.df_account['value'] + self.df_account['price'], 2)
        self.df_account['float'] = round(self.df_account['total'] - self.df_account['cost'], 2)
        self.df_account.columns = ['账户', '本金', '现金', '市值', '总资产', '浮动盈亏']
        self.df_account['利润率(%)'] = self.df_account['浮动盈亏'] / self.df_account['本金']


class showLogWindow(QWidget):
    def __init__(self,mainEngine):
        self.mainEngine = mainEngine
        self.count = 0
        super(showLogWindow,self).__init__(flags=Qt.WindowFlags())
        self.mainEngine.logSignal.connect(self.showMessage)
        # 创建多行文本框
        self.textEdit_left = QTextEdit()
        self.textEdit_right = QTextEdit()
        self.btn = QPushButton("清\n空\n日\n志")
        # 实例化水平布局
        layout = QHBoxLayout()
        # 相关控件添加到垂直布局中
        layout.addWidget(self.textEdit_left)
        layout.addWidget(self.textEdit_right)
        layout.addWidget(self.btn)
        self.btn.clicked.connect(self.clearText)
        # 设置布局
        self.setLayout(layout)

    def showMessage(self,message):
        # 以文本的形式输出到多行文本框

        self.count += 1
        x = math.modf(self.count/2)[0]
        if x == 0.5:
            pre_text_left = self.textEdit_left.toPlainText()
            self.textEdit_left.setPlainText(pre_text_left + message + '\n')
        else:
            pre_text_right = self.textEdit_right.toPlainText()
            self.textEdit_right.setPlainText(pre_text_right + message + '\n')

    def clearText(self):
        self.textEdit_left.setPlainText("")
        self.textEdit_right.setPlainText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle(QStyleFactory.create("WindowsXP"))
    win = SearchDB('历史单')
    win.show()
    sys.exit(app.exec_())
