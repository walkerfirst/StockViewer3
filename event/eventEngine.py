from queue import Queue, Empty
from datetime import datetime
from threading import *
from event.eventType import *


"""
事件管理类代码
事件驱动的简明讲解: https://www.jianshu.com/p/2290bfbd75dd
事件驱动的Python实现 : https://www.jianshu.com/p/a605fab0ab11
"""

class EventManager(object):

    def __init__(self):
        """ 初始化事件管理类"""
        # 事件对象列表
        self.__eventQueue = Queue()
        # 事件管理器开关
        self.__active = False
        # 事件处理线程
        self.__thread = Thread(target=self.__Run)
        self.count = 0


        # 这里的__handlers 是一个字典，用于保存对应的事件的相应函数
        # 每个键对应的值是一个列表， 列表中保存了对该事件的相应函数
        self.__handlers = {}

    def __Run(self):
        """ 引擎运行 """
        print("eventEngine is Running".format(self.count))

        while self.__active == True:
            try:
                # 获取事件的阻塞事件设置为1s
                event = self.__eventQueue.get(block=True, timeout=2)
                self.__EventProcess(event)
            except Empty:
                pass

    def __EventProcess(self, event):
        """ 处理事件 """
        # print("{}_EventProcess".format(self.count))
        # 检查是否存在对该事件进行监听的处理函数
        if event.type_ in self.__handlers:
            # 如果存在， 则按照顺序将事件传递给处理函数进行执行
            # print(event.type_)
            for handler in self.__handlers[event.type_]:
                # print('1',datetime.now())
                handler(event)
                # print('2',datetime.now())
        self.count += 1

    def Start(self):
        """启动"""
        print("eventEngine Start...".format(self.count))
        # 将事件管理器设置为启动
        self.__active = True
        # 启动事件处理线程
        self.__thread.start()

    def Stop(self):
        """停止"""
        print("eventEngine is Stop".format(self.count))
        # 将事件管理器设置为停止
        self.__active = False
        # 等待事件处理线程退出
        self.__thread.join()


    def AddEventListener(self, type_, handler):
        """ 绑定事件和监听器处理函数"""
        # print("{}_AddEventListener".format(self.count))
        # print(type_)
        # 尝试获取该事件类型队形的处理函数列表， 若无则创建
        try:
            handlerList = self.__handlers[type_]
        except KeyError:
            handlerList = []

        self.__handlers[type_] = handlerList
        # 若要注册的处理器不在该事件处理器的处理器列表中， 则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)

        # print(self.__handlers)
        self.count += 1

    def RemoveEventListener(self, type_, handler):
        """ 移除监听器的处理函数 """
        # print('{}_RemoveEventListener'.format(self.count))
        try:
            handlerList = self.__handlers[type_]
            # 如果函数存在于列表中，则移除
            if handler in handlerList:
                handlerList.remove(handler)
            # 如果函数列表为空，则从引擎中移除该事件类型
            if not handlerList:
                del self.__handlers[type_]
        except KeyError:
            pass
        self.count += 1

    def SendEvent(self, event):
        """ 发送事件，向事件队列中存入事件"""
        # print('{}_SendEvent'.format(self.count))
        # print(event.type_)
        # try:
        #     print(event.dict['data'])
            # print(event.type_)
        # except:
        #     pass
        self.__eventQueue.put(event)
        self.count+=1

class Event:
    """ 事件类型 """
    def __init__(self,type_=None):
        self.type_ = type_  # 事件类型
        self.dict = {}      # 字典用于保存具体事件数据