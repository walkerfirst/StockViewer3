# Author: Nike Liu
import sys
# sys.path.append('..')
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow
from MainEngine import MainEngine
from event.eventEngine import EventManager
import time


class Run(object):
    def __init__(self):
        start = time.time()
        self.ee = EventManager()
        self.me = MainEngine(self.ee)
        self.start()
        end = time.time()
        start_time = round(end - start,2)
        self.me.logSend('本次启动用时: %s s' % start_time)

    # def init_data(self):
    #     import tushare as ts
        # code = ['000001','600618']
        # df = ts.get_realtime_quotes(code)  # Single stock symbol
        # print(df)

        # df = ts.get_tick_data('002463', date='2019-09-11', src='tt')
        # print(df.tail(20))

    def start(self):
        # 在Application设置窗口样式，则对所有窗口有效
        # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        win = MainWindow(self.me)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyleSheet("#MainWindow{background-color: yellow}")
    win = Run()
    sys.exit(app.exec_())