"""
显示K线图
"""
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow
import datetime
import pyqtgraph as pg
import tushare as ts

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Kchart_MainWindow(QMainWindow):

    def __init__(self,code,name):
        self.code = code
        self.name = name
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("K Chart"))
        MainWindow.resize(1300, 800)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)

        self.drawChart = DrawChart(code=self.code,ktype='D')
        self.verticalLayout_2.addWidget(self.drawChart.pyqtgraphDrawChart())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "%s (%s)日线 k 线图" %(self.name,self.code), None))

class DrawChart():

    def __init__(self, code, start=str(datetime.date.today() - datetime.timedelta(days=200)), end=str(datetime.date.today() + datetime.timedelta(days=1)), ktype='D'):
        self.code = code
        self.start = start
        self.end = end
        self.ktype = ktype
        self.data_list, self.t = self.getData()

    def pyqtgraphDrawChart(self):
        try:
            self.item = CandlestickItem(self.data_list)
            self.xdict = {0: str(self.hist_data.index[0]).replace('-', '/'),
                          int((self.t + 1) / 3) - 1: str(self.hist_data.index[int((self.t + 1) / 3)])[-5:].replace('-', '/'),
                          int((self.t + 1) / 2) - 1: str(self.hist_data.index[int((self.t + 1) / 2)])[-5:].replace('-', '/'),
                          int((self.t + 1) / 3)*2 - 1: str(self.hist_data.index[int((self.t + 1) / 3)*2])[-5:].replace('-', '/'),
                          self.t - 3: str(self.hist_data.index[-1])[-5:].replace('-', '/')}
            self.stringaxis = pg.AxisItem(orientation='bottom')
            self.stringaxis.setTicks([self.xdict.items()])
            self.plt = pg.PlotWidget(axisItems={'bottom': self.stringaxis}, enableMenu=False)

            self.plt.addItem(self.item)
            # self.plt.showGrid(x=True, y=True)

            return self.plt
        except:
            return pg.PlotWidget()

    def getData(self):
        self.start = str(datetime.date.today() - datetime.timedelta(days=150))
        self.end = str(datetime.date.today() + datetime.timedelta(days=1))
        self.hist_data = ts.get_hist_data(self.code, self.start, self.end, self.ktype).sort_index()[-150:]
        # print(self.hist_data.columns)
        self.hist_data = self.hist_data[
            ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5','ma20']]
        volume_last = self.hist_data.iloc[-1]['volume']
        # 先把以date为index转成列
        self.hist_data = self.hist_data.reset_index(drop=False)
        # 获取历史数据的最新日期
        date_hist = self.hist_data.iloc[-1]['date']

        # print(self.hist_data[['open','close','low','p_change']])
        # 获取当日tick数据
        tick = ts.get_realtime_quotes(self.code)
        # 获取tick数据的最新日期
        date_tick = tick.iloc[-1]['date']
        # 得到明天日期（字符串格式）
        next_date = datetime.datetime.strptime(date_tick,'%Y-%m-%d') + datetime.timedelta(days=1)
        next_date = next_date.strftime('%Y-%m-%d')
        # 数据格式转换
        tick = tick[['open', 'price', 'low','volume','high', 'pre_close']].astype('float')
        # print(tick)
        tick.rename(columns={'price':'close'}, inplace=True)
        # 获取需要的数据
        series = tick.iloc[0]
        open = series['close']
        close = open * 0.95
        # 把新编制的数据添加到dataframe中
        new_data = {'open':open, 'close':close, 'low':close,'volume':volume_last,'high':open,'pre_close':open}
        tick = tick.append(new_data, ignore_index=True,sort=False)
        # 必要的计算
        tick['price_change'] = tick['close']-tick['pre_close']
        tick['p_change'] = round(tick['price_change']/tick['pre_close']*100,2)
        tick = tick.drop(['pre_close'],axis=1)
        self.hist_data = self.hist_data.append(tick, ignore_index=False,sort=False)
        # 判断是否历史数据中与当日tick数据重复，并给缺失的数据赋值
        if date_hist == date_tick:
            self.hist_data = self.hist_data.drop(tick.index[-2])
        else:
            self.hist_data.loc[0, 'ma5'] = self.hist_data['close'].rolling(5).mean().iloc[-2]
            # self.hist_data.loc[0, 'ma10'] = self.hist_data['close'].rolling(10).mean().iloc[-2]
            self.hist_data.loc[0, 'ma20'] = self.hist_data['close'].rolling(20).mean().iloc[-2]
            self.hist_data.loc[0, 'date'] = date_tick
        self.hist_data.loc[1, 'ma5'] = self.hist_data['close'].rolling(5).mean().iloc[-1]
        # self.hist_data.loc[1, 'ma10'] = self.hist_data['close'].rolling(10).mean().iloc[-1]
        self.hist_data.loc[1, 'ma20'] = self.hist_data['close'].rolling(20).mean().iloc[-1]
        self.hist_data.loc[1, 'date'] = next_date
        self.hist_data['ma50'] = self.hist_data['close'].rolling(50).mean()

        # 填充缺失的数据（以最新上一行数据填充）
        self.hist_data = self.hist_data.fillna(method='ffill')
        # 重设回原来的index
        self.hist_data = self.hist_data.set_index('date')
        # 给数据列排序，以便后面使用。不排序会出错
        self.hist_data = self.hist_data[['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change',
       'ma5', 'ma20', 'ma50']]
        # ma50 缺失值用0填充
        self.hist_data = self.hist_data.fillna(0)

        # 获取data list
        data_list = []
        t = 0
        for dates, row in self.hist_data.iterrows():
            open, high, close, low, volume, price_change, p_change, ma5, ma20, ma50 = row[:10]
            datas = (t, open, close, low, high, volume, price_change, p_change, ma5, ma20, ma50)
            data_list.append(datas)
            t += 1
        return data_list, t

class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        prema5 = 0
        prema20 = 0
        prema50 = 0
        for (t, open, close, min, max, volume, price_change, p_change, ma5, ma20, ma50) in self.data:
            if open > close:
                p.setPen(pg.mkPen('g'))
                p.setBrush(pg.mkBrush('g'))
            else:
                p.setPen(pg.mkPen('r'))
                p.setBrush(pg.mkBrush('r'))
            # 这里处理一下，防止出现奇点
            if min == max:
                max = max + 0.0001
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
            if prema5 != 0:
                p.setPen(pg.mkPen('w'))
                p.setBrush(pg.mkBrush('w'))
                p.drawLine(QtCore.QPointF(t-1, prema5), QtCore.QPointF(t, ma5))
            prema5 = ma5
            if prema20 != 0:
                p.setPen(pg.mkPen('c'))
                p.setBrush(pg.mkBrush('c'))
                p.drawLine(QtCore.QPointF(t-1, prema20), QtCore.QPointF(t, ma20))
            prema20 = ma20
            if prema50 != 0:
                p.setPen(pg.mkPen('m'))
                p.setBrush(pg.mkBrush('m'))
                p.drawLine(QtCore.QPointF(t-1, prema50), QtCore.QPointF(t, ma50))
            prema50 = ma50
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Kchart_MainWindow(code='603180',name='char')
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
