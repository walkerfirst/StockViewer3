# Author: Nike Liu

from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel,  QGridLayout, QLineEdit,QMessageBox
from trading.update_records_from_xls_to_access import ProcessTrading
from PyQt5.QtGui import QIcon
from datetime import datetime
from setting.account import Account

class Trading(QWidget):
    def __init__(self,data, me):
        self.data = data
        self.mainEngine = me
        super(Trading,self).__init__()
        self.code = self.data[0]
        self.name = self.data[1]
        self.option = self.data[2]
        self.account = self.data[3]
        self.initUi()

    def initUi(self):
        self.setWindowTitle("%s窗口" % self.option)
        self.setWindowIcon(QIcon('./res/draw.png'))
        layout = QGridLayout()
        self.setGeometry(600, 600, 450, 600)
        codeLabel = QLabel("代码")
        self.codeLineEdit = QLineEdit(self.code)
        nameLabel = QLabel("名称")
        self.nameLineEdit = QLineEdit(self.name)
        qtyLabel = QLabel("数量")
        self.qtyLineEdit = QLineEdit("100")
        priceLabel = QLabel("交易价格")
        self.priceLineEdit = QLineEdit("1")

        dateLabel = QLabel("日期")
        today = datetime.now().strftime('%Y-%m-%d')
        self.dateLineEdit = QLineEdit(today)
        accountLabel = QLabel("账号")
        self.accountBox =QLineEdit(self.account)
        # 下来列表格式
        # self.accountBox = QComboBox()
        # self.accountBox.addItem('华鑫',"HX_L")
        # self.accountBox.addItem('国联',"GL_J")
        # self.accountBox.addItem('其他',"GF_L")
        self.cashLineEdit = QLineEdit('0')
        cashLabel = QLabel("账户余额")

        # layout.setSpacing(10)
        layout.addWidget(codeLabel,0,0)
        layout.addWidget(self.codeLineEdit,0,1)
        layout.addWidget(nameLabel,1,0)
        layout.addWidget(self.nameLineEdit,1,1)
        layout.addWidget(qtyLabel, 2, 0)
        layout.addWidget(self.qtyLineEdit, 2, 1)
        layout.addWidget(priceLabel, 3, 0)
        layout.addWidget(self.priceLineEdit, 3, 1)
        layout.addWidget(dateLabel, 4, 0)
        layout.addWidget(self.dateLineEdit, 4, 1)
        layout.addWidget(accountLabel, 5, 0)
        layout.addWidget(self.accountBox, 5, 1)
        # layout.addWidget(cashLabel, 6, 0)
        # layout.addWidget(self.cashLineEdit, 6, 1)

        layout.setColumnStretch(1, 10)
        confirm_Btn = QPushButton('确定')
        cancle_Btn = QPushButton('取消')

        cancle_Btn.clicked.connect(self.close)
        confirm_Btn.clicked.connect(self.addNum)
        layout.addWidget(confirm_Btn)
        layout.addWidget(cancle_Btn)
        self.setLayout(layout)

    def addNum(self):

        box = QMessageBox(QMessageBox.Warning, "警告框", "确定提交")
        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
        qno = box.addButton(self.tr("取消"), QMessageBox.NoRole)
        box.exec_()
        if box.clickedButton() == qyes:
            code = self.codeLineEdit.text()
            name = self.nameLineEdit.text()  # 获取文本框内容
            qty = int(self.qtyLineEdit.text())
            price = float(self.priceLineEdit.text())
            # cash = float(self.cashLineEdit.text())
            if qty == 0 or price == 0:
                QMessageBox.about(self, "对话框", "请填写必要信息！")
            else:
                _date = self.dateLineEdit.text()
                # 获取下来框的值
                # account = self.accountBox.itemText(self.accountBox.currentIndex())  # 获取下来框的文本
                account = self.accountBox.text()
                amount = price * qty
                tax = 0
                # 获取不同账号的费率
                fei_rate = Account[account]['fei']
                fei_etf_rate = Account[account]['fei_etf']
                min_fei = Account[account]['min_fei']

                # 针对普通股情况
                fei = max(round(amount * fei_rate,2),min_fei)
                # 针对ETF情况
                if code[0] == '1' or code[0] == '5':
                    fei = max(round(amount * fei_etf_rate,2),min_fei)

                # 计算税率
                if self.option == '卖出' or '中签卖出':
                    tax = round(amount * 0.001,2)
                    if code[0] == '1' or code[0] == '5':
                        tax = 0

                trading_data = {'date':_date,'code':code,'name':name,'option':self.option,'qty':qty,'price':price,
                                'fei':fei,'tax':tax,'amount':amount,'account':account}
                # print('trading',trading_data)

                if self.option == '卖出':
                    ProcessTrading(trading_data).sell_ation()
                elif self.option == '买入':
                    ProcessTrading(trading_data).buy_ation()

                elif self.option == '中签卖出':
                    if "债" in name:
                        cost = 100
                    else:
                        cost = float(self.data[4])
                    amount = round((price - cost)*qty - tax - fei,2)
                    trading_data = {'date': _date, 'code': code, 'name': name, 'option': self.option, 'qty': qty,
                                    'price': price,'fei': fei, 'tax': tax, 'amount': amount, 'account': account}

                    # print(self.data,trading_data)
                    ProcessTrading(trading_data).ZX_ation()
                elif self.option == '现金红利':
                    trading_data = {'date': _date, 'code': code, 'name': name, 'option': self.option, 'qty': qty,
                                    'price': price,'fei': fei, 'tax': tax, 'amount': price, 'account': account}
                    ProcessTrading(trading_data).hongli_ation()

                # QMessageBox.about(self, "对话框", "%s处理已完成！" % self.option)

                # 发送账号变动event
                self.mainEngine.tradeEvent(trade_dict=trading_data)
                self.close()
        else:
            return


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    data = ['002624','完美']
    win = Trading(data)
    win.show()
    sys.exit(app.exec_())
