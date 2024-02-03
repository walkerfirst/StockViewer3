import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        lbl1 = QLabel('我的世界你曾经来过', self)
        lbl1.move(15, 10)

        lbl2 = QLabel('CSND博客', self)
        lbl2.move(35, 40)

        lbl3 = QLabel('程序员', self)
        lbl3.move(55, 70)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('绝对定位')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())