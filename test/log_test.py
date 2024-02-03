import sys
from PyQt5.QtWidgets import QWidget,QPlainTextEdit,QVBoxLayout
import logging
from event.eventType import EVENT_LOG

# Uncomment below for terminal log messages
# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MyDialog(QWidget):
    def __init__(self, mainEngine,parent=None):
        super().__init__(parent)
        self.mainEngine = mainEngine
        self.mainEngine.registerHandler(type_=EVENT_LOG,handler=self.LogWindowshow)

        logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        layout = QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)

        self.setLayout(layout)

    def LogWindowshow(self,event):
        log_type = event.dict['log_type']
        log_message = event.dict['message']
        if log_type == 'info':
            logging.info(log_message)
        if log_type == 'debug':
            logging.debug(log_message)
        if log_type == 'error':
            logging.error(log_message)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    from MainEngine import MainEngine
    from event.eventEngine import EventManager
    from util.logger import QuantLogger
    ee = EventManager()
    me = MainEngine(ee)

    dlg = MyDialog(me)
    dlg.show()
    dlg.raise_()
    logger = QuantLogger(me,'test')
    logger.info('test ok')
    logger.debug('debug')
    logger.error('error')

    sys.exit(app.exec_())