#  -*- coding: utf-8 -*-

from datetime import datetime
import time
from DataEngine import DataEngine


def is_trading_day():
    """检查当日是否为交易日"""
    date_ = datetime.now().strftime('%Y-%m-%d')
    right_now = int(time.strftime("%H%M%S"))
    check = True
    symbols = ['399006']
    if right_now >= 90000:
        try:
            data = DataEngine().getTick(symbols)
            if not data.empty:
                date_tick = data.iloc[0]['date']
                if date_ != date_tick:
                    check = False
        except:
            pass
    return check

if __name__ == '__main__':
    x = is_trading_day()
    print(x)