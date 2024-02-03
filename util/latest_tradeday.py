# Author: Nike Liu
from util.tushare_pro import pro
from datetime import datetime,timedelta
def trade_days(start,end):
    data = pro.query('trade_cal', start_date=start, end_date=end,is_open='1')
    # exchange默认为上交所,start_date和end_date不是必填,is_open不填是全部,is_open可以使用0和1,0为不交易的日期,1为交易日
    trade_days = data['cal_date'].tolist()
    # print(trade_days)
    latest_day = trade_days[-1]
    return trade_days,latest_day

today = datetime.today()
start = today - timedelta(20)
start_date = start.strftime('%Y%m%d')
end_date = today.strftime('%Y%m%d')

trade_days,latest_day = trade_days(start=start_date,end=end_date)
# print(trade_days)