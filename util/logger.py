# -*- coding: utf-8 -*-

import logging.handlers
import sys,os
import time
from event.eventType import *

# father_path = os.path.abspath(os.path.dirname(os.getcwd()))
father_path = os.getcwd()

time = time.strftime("%Y%m%d-%H-%M", time.localtime())

class QuantLogger:
    def __init__(self,mainEngine, name):
        # 业务日志的配置
        self.mainEngine = mainEngine

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        format = logging.Formatter('[%(asctime)s[' + name + '] %(levelname)s: %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(father_path + '/logs/info.log', 'D')
        handler.setFormatter(format)
        self.logger.addHandler(handler)

        # 错误日志的配置
        self.errorLogger = logging.getLogger("ERROR")
        self.errorLogger.setLevel(logging.ERROR)
        errorFormatter = logging.Formatter('[%(asctime)s[' + name + '] %(levelname)s: %(message)s')
        errorHandler = logging.handlers.TimedRotatingFileHandler(father_path + '/logs/error.log', 'D')
        errorHandler.setFormatter(errorFormatter)
        self.errorLogger.addHandler(errorHandler)

        # 调试日志的配置
        self.debugLogger = logging.getLogger("DEBUG")
        self.debugLogger.setLevel(logging.DEBUG)
        debugFormatter = logging.Formatter('[%(asctime)s[' + name + '] %(levelname)s: %(message)s')
        debugHandler = logging.handlers.TimedRotatingFileHandler(father_path + '/logs/debug.log', 'D')
        debugHandler.setFormatter(debugFormatter)
        self.debugLogger.addHandler(debugHandler)

    def info(self, message, *args):
        self.logger.info(message, *args)
        info_dict = {}
        info_dict['log_type'] = 'info'
        info_dict['message'] = message
        self.mainEngine.sendEvent(type_=EVENT_LOG,event_dict=info_dict)

    def error(self, message, *args):
        self.errorLogger.error(message, *args, exc_info=True)
        info_dict = {}
        info_dict['log_type'] = 'error'
        info_dict['message'] = message
        self.mainEngine.sendEvent(type_=EVENT_LOG, event_dict=info_dict)

    def debug(self, message, *args):
        self.debugLogger.debug(message, *args)
        info_dict = {}
        info_dict['log_type'] = 'debug'
        info_dict['message'] = message
        self.mainEngine.sendEvent(type_=EVENT_LOG, event_dict=info_dict)

