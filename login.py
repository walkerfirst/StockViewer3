import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap,  QFont, QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QDesktopWidget, QHBoxLayout, QFormLayout, \
    QPushButton, QLineEdit,QMessageBox
import base64

class LoginForm(QWidget):
    def __init__(self,me):
        self.mainEngine = me
        super().__init__()
        self.count = 0
        self.initUI()

    def initUI(self):

        self.setObjectName("loginWindow")
        self.setStyleSheet('#loginWindow{background-color:white}')
        self.setFixedSize(650, 400)
        self.setWindowTitle("登录")
        self.setWindowIcon(QIcon('./res/persons.png'))
        self.text = "股票管理系统  用户登录"

        # 添加顶部logo图片
        pixmap = QPixmap("./res/login.jpg")
        scaredPixmap = pixmap.scaled(650, 140)
        label = QLabel(self)
        label.setPixmap(scaredPixmap)

        # 绘制顶部文字
        lbl_logo = QLabel(self)
        lbl_logo.setText(self.text)
        lbl_logo.setStyleSheet("QWidget{color:white;font-weight:600;background: transparent;font-size:30px;}")
        lbl_logo.setFont(QFont("Microsoft YaHei"))
        lbl_logo.move(150, 50)
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.raise_()

        # 登录表单内容部分
        login_widget = QWidget(self)
        login_widget.move(0, 140)
        login_widget.setGeometry(0, 140, 650, 260)

        hbox = QHBoxLayout()
        # 添加左侧logo
        logolb = QLabel(self)
        logopix = QPixmap('./res/files-and-folders.png')
        logopix_scared = logopix.scaled(100, 100)
        logolb.setPixmap(logopix_scared)
        logolb.setAlignment(Qt.AlignCenter)
        hbox.addWidget(logolb, 1)
        # 添加右侧表单
        fmlayout = QFormLayout()
        lbl_workerid = QLabel("用户名")
        lbl_workerid.setFont(QFont("Microsoft YaHei"))
        self.led_workerid = QLineEdit("admin")
        self.led_workerid.setFixedWidth(270)
        self.led_workerid.setFixedHeight(38)

        lbl_pwd = QLabel("密码")
        lbl_pwd.setFont(QFont("Microsoft YaHei"))
        self.led_pwd = QLineEdit("123")
        self.led_pwd.setEchoMode(QLineEdit.Password)
        self.led_pwd.setFixedWidth(270)
        self.led_pwd.setFixedHeight(38)

        btn_login = QPushButton("登录")
        btn_login.setFixedWidth(270)
        btn_login.setFixedHeight(40)
        btn_login.setFont(QFont("Microsoft YaHei"))
        btn_login.setObjectName("login_btn")
        btn_login.setStyleSheet("#login_btn{background-color:#2c7adf;color:#fff;border:none;border-radius:4px;}")
        btn_login.clicked.connect(self.check_login)

        fmlayout.addRow(lbl_workerid, self.led_workerid)
        fmlayout.addRow(lbl_pwd, self.led_pwd)
        fmlayout.addWidget(btn_login)
        hbox.setAlignment(Qt.AlignCenter)
        # 调整间距
        fmlayout.setHorizontalSpacing(20)
        fmlayout.setVerticalSpacing(12)

        hbox.addLayout(fmlayout, 2)

        login_widget.setLayout(hbox)

        self.center()
        self.show()

    def center(self):
        # 得到框架信息
        qr = self.frameGeometry()
        # 得到中心位置
        cp = QDesktopWidget().availableGeometry().center()
        # 框架中心与中心位置对齐
        qr.moveCenter(cp)
        # 自身窗口左上角与中心位置对齐
        self.move(qr.topLeft())

    def check_login(self):

        user = self.led_workerid.text()
        sn = self.led_pwd.text()
        # sn_encode = base64.b64encode(sn.encode("utf8"))
        sn_str = base64.b64decode('MTIz').decode("utf8")
        if user == "admin" and sn == sn_str:
            self.mainEngine.loginEvent()
            self.close()
        else:
            QMessageBox.about(self, "提示！", "用户名或者密码不对！")
            self.count += 1
            if self.count >= 3:
                self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LoginForm()

    sys.exit(app.exec_())