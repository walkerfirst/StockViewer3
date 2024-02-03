# Author: Nike Liu

from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel,  QGridLayout, QLineEdit,QMessageBox

class stcokprocess(QWidget):
    def __init__(self,data,me):
        self.data = data
        self.mainEngine = me
        super(stcokprocess,self).__init__()
        self.code = self.data[0]
        self.name = self.data[1]
        self.initUi()
    def initUi(self):
        self.setWindowTitle("填权处理窗口")
        layout = QGridLayout()
        self.setGeometry(600, 600, 400, 400)
        codeLabel = QLabel("代码")
        self.codeLineEdit = QLineEdit(self.code)
        nameLabel = QLabel("名称")
        self.nameLineEdit = QLineEdit(self.name)
        qtyLabel = QLabel("倍数")
        self.timeLineEdit = QLineEdit("")

        # layout.setSpacing(10)
        layout.addWidget(codeLabel,0,0)
        layout.addWidget(self.codeLineEdit,0,1)
        layout.addWidget(nameLabel,1,0)
        layout.addWidget(self.nameLineEdit,1,1)
        layout.addWidget(qtyLabel, 2, 0)
        layout.addWidget(self.timeLineEdit, 2, 1)
        layout.setColumnStretch(1, 10)
        save_Btn = QPushButton('确定')
        cancle_Btn = QPushButton('取消')
        cancle_Btn.clicked.connect(self.close)
        save_Btn.clicked.connect(self.addNum)
        layout.addWidget(save_Btn)
        layout.addWidget(cancle_Btn)
        self.setLayout(layout)

    def addNum(self):
        code = self.codeLineEdit.text()
        name = self.nameLineEdit.text()  # 获取文本框内容
        time = float(self.timeLineEdit.text())
        # print(time, type(time))

        read_sql = "select ID,code,名称,买入价,数量 from buy where 结单 = 'N' AND code = '" + code + "'"
        df = self.mainEngine.dbQurey(read_sql,columns=['id','code','name','cost','qty'])

        if df.index.size >0 and time > 0:
            df['cost'] = round(df['cost'] / time,2)
            df['qty'] = df['qty'] * time
        for index in df.index:
            data = df.iloc[index]
            id = str(data[0])
            cost = str(data[3])
            qty = str(data[4])

            update_sql = "UPDATE buy SET 买入价= '"+ cost +"',数量 = '"+ qty +"' WHERE ID ="+id
            self.mainEngine.excuteSQL(update_sql)
            # print('update is done')
        QMessageBox.about(self, "对话框", "填权处理已完成！")
        # 发送账号变动event
        self.mainEngine.tradeEvent(df)
        self.close()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = stcokprocess()
    win.show()
    sys.exit(app.exec_())
