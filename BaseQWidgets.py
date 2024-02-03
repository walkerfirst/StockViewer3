from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QObject
from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QBrush, QColor, QFont,QIcon
#from show_k_chart import Kchart_MainWindow
from model.DataFrameTableModel import pandasModel
from res import resource

class BaseStandardTable2(QWidget,QObject):
    """基于BaseStandardTable 的基类模型，基于QWidget,QObject两个基类。必须要QObject的原因为了pyqt信号发送"""

    tableheader = []
    def __init__(self):
        super(BaseStandardTable2, self).__init__()
        self.initModel()
        self.initUI()

    def initModel(self):
        # 定义数据模型
        self.model = QStandardItemModel(self)

        # 重新设置表格头的显示名称
        ColumnsNum = len(self.tableheader)
        if ColumnsNum > 0:
            for index in range(0, ColumnsNum):
                self.model.setHorizontalHeaderItem(index, QStandardItem(self.tableheader[index]))

    def initUI(self):

        # 设置表格布局
        layout = QHBoxLayout()
        self.tableView = QTableView()
        layout.addWidget(self.tableView)
        # 给表格控件设置数据模型
        self.tableView.setModel(self.model)
        self.tableView.setFont(QFont("Arial", 12))
        # 隐藏表格的列名称
        self.tableView.verticalHeader().hide()
        # 设置表格横向/纵向填满整个layout
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格宽度适合内容
        # self.tableView.resizeColumnsToContents()
        # 开启按列排序功能
        # self.tableView.setSortingEnabled(True)
        # 选择内容的行为：行高亮
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置表格交叉颜色
        self.tableView.setAlternatingRowColors(True)

        # 单击绑定槽函数
        # self.tableView.clicked.connect(self.showKChart)

        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        # self.tableView.clicked.connect(self.on_tableView_clicked)
        # delegate = TableDelegate()
        # self.tableView.setItemDelegate(delegate)
        self.setLayout(layout)

    def update_data_to_model(self,dataframe):
        """ 把dataframe数据关联到model"""
        try:
            # 更新model数据前，先清空之前的数据
            column_size = len(dataframe.columns)
            self.model.removeColumns(column_size, 0)
            # 这里不能用model获取行数，否则不准确
            row = dataframe.index.size
            self.model.removeRow(row)
            # 每次更新都要重新设置
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # 开始关联数据
            if not dataframe.empty:
                for index in dataframe.index:
                    data = dataframe.iloc[index]
                    col = len(data)
                    for i in range(0,col):
                        self.model.setItem(index, i, QStandardItem(str(data[i])))
                        # 设置对齐方式
                        self.model.item(index,i).setTextAlignment(Qt.AlignCenter)

        except Exception as e:
            print('BaseQW set model发生错误%s' % str(e))

    def setForeground(self,df,byname):
        """设置某一列的字体颜色  byname 为df的列名，根据这一列的值判断 """
        try:
            # 首先获取总行数
            if not df.empty:
                # 这里不能用model获取行数，否则不准确
                row = self.model.rowCount()
                columns = list(df.columns)
                # 根据列名得到列所在的序号
                column_number = columns.index(byname)
                for index in range(0,row):
                    wave = df.iloc[index][byname]
                    if wave > 0:
                        self.model.item(index, column_number).setForeground(QBrush(QColor("red")))
                    elif wave == 0:
                        self.model.item(index, column_number).setForeground(QBrush(QColor("white")))
                    else:
                        self.model.item(index, column_number).setForeground(QBrush(QColor("green")))
                    if byname == 'price':
                        self.model.item(index, column_number).setForeground(QBrush(QColor("orange")))

        except Exception as e:
            print('BaseQW set color 发生错误%s'%str(e))

    # def on_tableView_clicked(self, index):
    #     """
    #     单击显示图书详细信息
    #     当我们单击表格的时候，取得行号。
    #     因为我们的数据来源都是数据模型，我们就根据模型中第几行第几个字段取得相应的值
    #     """
    #     row = index.row()
    #     # print(self.model.record(row).value("code"))
    #     # 获取鼠标单击的单元格值
    #     print(self.model.item(row,1).text())
    #     # DetailTable().setdata(self.df)


    # def showKChart(self, index):
    #     row = index.row()
    #     # 获取鼠标单击的单元格值
    #     name = self.model.item(row, 1).text()
    #     if "汇总" not in name:
    #         code = self.model.item(row, 0).text()
    #         print(code)
    #         # self.kWindow = QtGui.QMainWindow()
    #         # self.ui = Kchart_MainWindow(code=code, name=name)
    #         # self.ui.setupUi(self.kWindow)
    #         # self.kWindow.show()

class BaseDFTable(QWidget):
    """利用DataFrame新建Qtableview的显示控件"""
    columnName = []

    def __init__(self):
        # self.df = dataframe
        super(BaseDFTable, self).__init__()
        self.initUI()

    def initUI(self):

        # 水平布局，初始表格5*3，添加到布局
        layout = QHBoxLayout()
        self.dataView = QTableView()
        self.dataView.setObjectName("dataView")
        self.setWindowIcon(QIcon(':/draw.png'))
        font = self.dataView.horizontalHeader().font()  # 获取当前表头的字体
        font.setFamily("微软雅黑")  # 修改字体设置
        self.dataView.horizontalHeader().setFont(font)  # 重新设置表头的字体

        # 设置表头背景色
        self.dataView.horizontalHeader().setStyleSheet("QHeaderView::section{background:#B0C4DE;}")

        # 设置表格横向/纵向填满整个layout
        self.dataView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.dataView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        # self.dataView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格列与行尺寸适用内容
        self.dataView.resizeColumnsToContents()
        self.dataView.resizeRowsToContents()
        # 选择内容的行为：行高亮
        # self.dataView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 连接单击槽函数
        # self.dataView.clicked.connect(self.on_tableView_clicked)
        # 允许右键产生菜单，如果不设为CustomContextMenu,无法使用customContextMenuRequested
        self.dataView.setContextMenuPolicy(Qt.CustomContextMenu)

        # 将右键菜单绑定到槽函数showContextMenu
        # self.dataView.customContextMenuRequested.connect(self.showContextMenu)

        # 将右键菜单绑定到槽函数generateMenu
        # self.dataView.customContextMenuRequested.connect(self.generateMenu)

        # 开启按列排序功能
        self.dataView.setSortingEnabled(True)

        # 设置列名隐藏
        self.dataView.verticalHeader().setVisible(False)
        # 设置行名隐藏
        # self.dataView.horizontalHeader().setVisible(False)

        # 隐藏不需要的列，必须放在在setModel之后才能生效，从第0列开始
        # self.dataView.hideColumn(1)
        self.dataView.setFont(QFont("Arial", 10))

        # 设置表格交叉颜色
        self.dataView.setAlternatingRowColors(True)

        # 将表格控件添加到layout中去
        layout.addWidget(self.dataView)

        # self.dataView.clicked.connect(self.on_tableView_clicked)
        # 设置layout
        self.setLayout(layout)

    def update_model(self,df):
        if not df.empty:
            if '日期' in df.columns:

                df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
                df = df.sort_values(by='日期', ascending=False)

                if '名称' in df.columns:
                    df = df.sort_values(by=['日期', '名称'], ascending=False)
            if 'index' in df.columns:
                df = df.drop(['index'], axis=1)
            if '盈利' in df.columns:
                df['盈利'] = df['盈利'].astype('int')
            if '利润率(%)' in df.columns:
                df['利润率(%)'] = round(df['利润率(%)'] * 100, 1)
            df = df.replace("NaT", "总计：")
            if '数量' in df.columns:
                df['数量'] = df['数量'].astype('int')
            df = df.reset_index(drop=True)
        self.model = pandasModel(df)
        self.dataView.setModel(self.model)

        # print(u'处理每秒触发的计时器事件：%s' % str(datetime.now()))
        if '涨跌幅(%)' in df.columns:
            self.setColumnColor(columnName='涨跌幅(%)')

        if '利润率(%)' in df.columns:
            self.setColumnColor(columnName='利润率(%)')

    def setCellColor(self, row, column,color):
        """color:Qt.darkGreen"""
        self.model.change_color(row, column, QBrush(color))

    def setColumnWidth(self,column,size):
        self.dataView.setColumnWidth(column,size)

    def setColumnColor(self,columnName):

        row = self.model.rowCount()
        self._df = self.model._data
        column = self._df.columns.get_loc(columnName)
        for index in range(0, row):
            wave = self._df.iloc[index,column]
            if wave > 0:
                self.setCellColor(index,column,Qt.red)
            elif wave < 0:
                self.setCellColor(index, column, Qt.darkGreen)

    def resetColumnName(self,df,NewName:list):
        self._df = df
        index = self._df.columns
        count = min(len(index),len(NewName))
        for i in range(0,count):
            self._df.rename(columns={index[i]: NewName[i]}, inplace=True)
        return self._df

    def on_tableView_clicked(self, index):
        """
        单击获取行信息
        """
        row = index.row()
        name = self.model._data.iloc[row][1]
        # print(self.df[self.df['代码'] == self.model._data.iloc[row]['代码']])
        # print(self.model.flags(index))

        if name != "汇总":
            code = self.model._data.iloc[row][0]
            # print(code)
            #if code is not None:
                #self.kWindow = QMainWindow()
                #self.ui = Kchart_MainWindow(code=code, name=name)
                #self.ui.setupUi(self.kWindow)
                #self.kWindow.show()

    def showContextMenu(self):  # 创建右键菜单
        self.dataView.contextMenu = QMenu(self)

        # self.actionA = self.view.contextMenu.exec_(self.mapToGlobal(pos))  # 1
        self.dataView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.actionA = self.dataView.contextMenu.addAction('动作a')
        self.actionA.triggered.connect(self.actionHandler)

        self.action2 = self.dataView.contextMenu.addAction('动作2')
        self.action2.triggered.connect(self.actionHandler)

        # self.view.contextMenu.move(self.pos())  # 3
        self.dataView.contextMenu.show()

    def actionHandler(self):
        # 计算有多少条数据，默认-1,
        row_num = -1
        for i in self.dataView.selectionModel().selection().indexes():
            row_num = i.row()

        print('动作a', row_num)

        print('你选了选项一，当前行文字内容是：')

