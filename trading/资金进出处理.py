# Author: Nike Liu

from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel,  QGridLayout, QLineEdit,QMessageBox,QComboBox
from PyQt5.QtGui import QIcon
from datetime import datetime

class ZJProcess(QWidget):
    def __init__(self,data,me):
        self.data = data
        self.mainEngine = me
        super(ZJProcess,self).__init__()
        self.account = self.data[3]
        self.initUi()

    def initUi(self):
        self.setWindowTitle("资金处理处理窗口")
        self.setWindowIcon(QIcon('./res/draw.png'))
        layout = QGridLayout()
        self.setGeometry(600, 600, 600, 600)
        accountLabel = QLabel("账号")
        self.accountLineEdit = QLineEdit(self.account)
        CZLabel = QLabel('操作')
        self.CZBox = QComboBox()
        self.CZBox.addItem('增加资金',1)
        self.CZBox.addItem('减少资金',-1)
        amountLabel = QLabel('金额')
        self.amountLineEdit = QLineEdit('')
        dateLabel = QLabel("日期")
        today = datetime.now().strftime('%Y-%m-%d')
        self.dateLineEdit = QLineEdit(today)

        markLabel = QLabel("备注")
        self.markLineEdit = QLineEdit('')

        # layout.setSpacing(10)
        layout.addWidget(accountLabel,0,0)
        layout.addWidget(self.accountLineEdit,0,1)
        layout.addWidget(CZLabel,1,0)
        layout.addWidget(self.CZBox,1,1)
        layout.addWidget(amountLabel, 2, 0)
        layout.addWidget(self.amountLineEdit, 2, 1)
        layout.addWidget(dateLabel, 3, 0)
        layout.addWidget(self.dateLineEdit, 3, 1)
        layout.addWidget(markLabel,4,0)
        layout.addWidget(self.markLineEdit,4,1)
        layout.setColumnStretch(1, 10)
        save_Btn = QPushButton('确定')
        cancle_Btn = QPushButton('取消')
        cancle_Btn.clicked.connect(self.close)
        save_Btn.clicked.connect(self.addNum)
        layout.addWidget(save_Btn)
        layout.addWidget(cancle_Btn)
        self.setLayout(layout)

    def addNum(self):
        amount = float(self.amountLineEdit.text())
        account = self.accountLineEdit.text()
        date = self.dateLineEdit.text()
        caozuo = self.CZBox.itemData(self.CZBox.currentIndex()) # 获取下来框的值
        accDict = DataEngine().accDict[account]
        mark = self.markLineEdit.text()
        cash = accDict['cash']
        cost = accDict['cost']

        # print(caozuo,type(caozuo),type(cash))
        if caozuo == 1:
            new_cash = str(round(cash + amount,2))
            new_cost = str(round(cost + amount,2))
        else:
            new_cash = str(round(cash - amount,2))
            new_cost = str(round(cost - amount,2))
            amount = 0 - amount
        # print(cash,new_cash)
            # 更新账户信息
        update_sql = "UPDATE 账户 SET cash= '"+ new_cash +"',投入本金 = '"+ new_cost +"' WHERE code = '"+ account +"'"
        self.mainEngine.excuteSQL(update_sql)

        # 写入进出明细
        insert_sql = "INSERT INTO 资金明细(日期,金额,account,备注) VALUES ('" + date + "','" + str(amount) + "'," \
                                " '" + account + "','" + mark + "')"
        self.mainEngine.excuteSQL(insert_sql)

        QMessageBox.about(self, "对话框", "资金处理已完成！")
        self.close()
        # 发送账号变动event
        self.mainEngine.tradeEvent(amount)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    win = ZJProcess()
    win.show()
    sys.exit(app.exec_())
