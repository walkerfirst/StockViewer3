from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow,QAction,QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from MainQWidgets import Myhold2,StatusForm,IndexTable2,SearchDB,showLogWindow
from setting.symbols import class_symbols,index_symbols
import qdarkstyle
from res import resource
from login import LoginForm


class MainWindow(QMainWindow):
    """主窗口布局设置"""

    def __init__(self,mainEngine):
        super(MainWindow, self).__init__()
        # 初始化引擎、数据和UI
        self.mainEngine = mainEngine

        self.initUi()

    def initUi(self):
        """初始化界面"""
        # path = os.getcwd().rsplit('\\')[-1]
        self.setWindowTitle('智谷短线策略交易引擎 v1.0')
        # self.setWindowOpacity(0.9) # 设置窗口透明度
        self.resize(1500,900)
        # 设置程序的图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/files-and-folders.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        self.font = QtGui.QFont()
        self.font.setFamily("Arial")  # 括号里可以设置成自己想要的其它字体
        self.font.setPointSize(12)  # 括号里的数字可以设置成自己想要的字体大小
        self.setFont(self.font)
        # 在这里设置窗口的样式，只对本窗口有效。在Application设置则对所有窗口有效
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # load 菜单栏
        # self.initMenu()

        # load 工具栏
        self.initBar()
        # 主控件
        self.initTable()
        self.MainLayout()

        # load 状态栏
        self.initStatusBar()

        # 最大化窗口
        self.showMaximized()

        # loading登录窗口
        self.login = LoginForm(self.mainEngine)

    def initMenu(self):
        """初始化菜单"""
        # 设置菜单项
        bar = self.menuBar()
        self.Menu = bar.addMenu("文件")
        self.signUpAction = QAction("注册", self)
        self.close = QAction("退出", self)

        self.Menu.addAction(self.signUpAction)
        self.Menu.addAction(self.close)
        self.close.triggered.connect(self.closeEvent)

        self.query = bar.addMenu("操作")
        self.update_price = QAction("更新数据库最新价格", self)
        self.stockprocess = QAction("填权处理", self)
        self.query.addAction(self.update_price)
        self.query.addAction(self.stockprocess)

        self.update_price.triggered.connect(self.run_update)
        self.stockprocess.triggered.connect(self.stockprocessprice)

        self.connet = bar.addMenu("链接数据")
        self.start_timer = QAction('开始更新',self)
        self.stop_timer = QAction('停止更新',self)
        self.connet.addAction(self.start_timer)
        self.connet.addAction(self.stop_timer)
        # self.start_timer.triggered.connect(self.createQtimer)
        self.stop_timer.triggered.connect(self.timer_stop)

    def initBar(self):

        """初始化工具栏"""
        tb1 = self.addToolBar("File")
        start = QAction(QIcon(':/start.png'), "开始", self)
        tb1.addAction(start)
        start.triggered.connect(lambda: self.mainEngine.createQtimer())

        stop = QAction(QIcon(':/pause.png'), "暂停", self)
        tb1.addAction(stop)
        stop.triggered.connect(self.mainEngine.timer_stop)

        update = QAction(QIcon(':/update.png'), "更新", self)
        tb1.addAction(update)
        update.triggered.connect(self.run_update)

        import_data = QAction(QIcon(':/1-19122Q926010-L.png'), "导入数据", self)
        tb1.addAction(import_data)
        import_data.triggered.connect(self.import_data)

        save_data = QAction(QIcon(':/cloud-download2.png'), "保存收盘", self)
        tb1.addAction(save_data)
        save_data.triggered.connect(self.mainEngine.saveData)

        search_report = QAction(QIcon(':/1-1912302044060-L.png'), "搜索研报", self)
        tb1.addAction(search_report)
        search_report.triggered.connect(self.showSearch)

        search_history = QAction(QIcon(':/1-1912302044060-L.png'), "搜索历史", self)
        tb1.addAction(search_history)
        search_history.triggered.connect(self.showSearch_history)


        accountDetails = QAction(QIcon(':/Background.png'), "账户信息", self)
        tb1.addAction(accountDetails)
        accountDetails.triggered.connect(self.showAccount)

        quit = QAction(QIcon(':/poweroff2.png'), "退出", self)
        tb1.addAction(quit)
        quit.triggered.connect(self.close)

        tb1.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 给工具添加显示的layout
        # default.triggered.connect(self.DefaultLayout)
        # history.triggered.connect(self.TabWigde)

    def initTable(self):
        self.table_HX_L = Myhold2(self.mainEngine, account='HX_L')
        # self.table_GL_J = Myhold2(self.mainEngine,account='GL_J')
        # self.table_HT_L = Myhold2(self.mainEngine, account='HT_L')
        # self.table_ZH_F = Myhold2(self.mainEngine, account='ZH_F')

        self.table_index = IndexTable2(self.mainEngine,symbols=index_symbols)
        self.table_class = IndexTable2(self.mainEngine,symbols=class_symbols)
        self.table_log = showLogWindow(mainEngine=self.mainEngine)

    def MainLayout(self):
        """主窗口的显示设置"""

        self.HX_dock = self.create_dock(self.table_HX_L, "华鑫", QtCore.Qt.LeftDockWidgetArea)
        # self.GL_dock = self.create_dock(self.table_GL_J, "国联", QtCore.Qt.LeftDockWidgetArea)
        # self.HT_dock = self.create_dock(self.table_HT_L, "华泰", QtCore.Qt.LeftDockWidgetArea)
        # self.ZH_dock = self.create_dock(self.table_ZH_F, "中航", QtCore.Qt.LeftDockWidgetArea)
       # self.class_dock = self.create_dock(self.table_class, "板块ETF", QtCore.Qt.RightDockWidgetArea)
        #self.index_dock = self.create_dock(self.table_index, "重要指数", QtCore.Qt.RightDockWidgetArea)
      #  self.log_dock = self.create_dock(self.table_log,'日志',QtCore.Qt.RightDockWidgetArea)

        # 设置dock的最大高度和宽度
        # self.HX_dock.setMaximumHeight(750)
        # self.ZH_dock.setMaximumHeight(300)
        # self.HT_dock.setMaximumHeight(300)
       # self.index_dock.setMaximumHeight(450)
        #self.log_dock.setMaximumHeight(200)

       # self.class_dock.setMaximumWidth(1300)
        # 设置成选项卡格式
        # self.tabifyDockWidget(index_dock,HT_dock)
        # self.tabifyDockWidget(holding_dock,history_dock)
        # 发出通知？
        # class_dock.raise_()

    def create_dock(self, widget, name: str, area: int):
        """
        Initialize a dock widget.
        """
        dock = QtWidgets.QDockWidget(name)
        dock.setWidget(widget)
        dock.setObjectName(name)
        dock.setFeatures(dock.AllDockWidgetFeatures)
        # dock.setFeatures(dock.DockWidgetVerticalTitleBar)  # 标签栏竖排
        self.addDockWidget(area, dock)
        return dock

    def showSearch(self):
        """搜索研报记录"""
        self.showSearch = SearchDB('研报')
        self.showSearch.show()

    def showSearch_history(self):
        """搜索历史交易"""
        self.search_history = SearchDB('历史单')
        self.search_history.show()

    def closeEvent(self, event):
        """关闭窗口的确认动作"""
        box = QMessageBox(QMessageBox.Warning, "警告框", "确定关闭窗口？")
        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
        qno = box.addButton(self.tr("取消"), QMessageBox.NoRole)
        box.exec_()
        if box.clickedButton() == qyes:
            self.mainEngine.timer_stop()
            # 关闭窗口前需要处理的动作
            self.mainEngine.exit()
            app = QApplication.instance()
            # close window
            event.accept()
            print('窗口关闭')
            # 退出程序
            app.quit()
        else:
            event.ignore()
            # self.saveData()

    def run_update(self):
        """更新价格信息对话框"""
        from import_data.update_price_to_hold import updatePrice
        self.run_update = updatePrice()
        QMessageBox.about(self, "对话框", "更新已完成！")

    def showdialog(self):
        """状态栏对话框"""
        self.dialog = StatusForm(self.mainEngine)
        self.dialog.show()

    def import_data(self):
        """把exel交易数据导入到db中"""
        from trading.update_records_from_xls_to_access import update_records_to_access
        box = QMessageBox(QMessageBox.Warning, "警告框", "导入文件是否已更新？")
        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
        qno = box.addButton(self.tr("取消"), QMessageBox.NoRole)
        box.exec_()
        if box.clickedButton() == qyes:
            self.import_data = update_records_to_access()
        else:
            return

    def initStatusBar(self):
        """ 状态栏"""
        self.status = self.statusBar()
        # self.status.showMessage('实时更新的信息', 0)
        #  状态栏本身显示的信息 第二个参数是信息停留的时间，单位是毫秒，默认是0（0表示在下一个操作来临前一直显示）
        # self.lable = QLabel()

        self.comNum1 = StatusForm(self.mainEngine)
        self.status.addWidget(self.comNum1, stretch=1)

    def showAccount(self):
        from MainQWidgets import AccountDetails
        self.show_Account = AccountDetails(self.mainEngine)

if __name__ == "__main__":
    import sys
    from event.eventEngine import EventManager
    from MainEngine import MainEngine
    app = QApplication(sys.argv)
    ee = EventManager()
    me = MainEngine(ee)
    win = MainWindow(me)
    sys.exit(app.exec_())