# Author: Nike Liu
import sys
sys.path.append('..')
import tushare as ts
from util.database import conn
from util.latest_tradeday import start_date,latest_day

class updatePrice():
    def __init__(self):
        self.cursor = conn.cursor()
        self.updateHold()
        self.updateHistory()

    def updateHold(self):
        # 从access中提取持仓股的list
        hold_table = "SELECT * FROM 持仓概览"
        # 将查询语句执行生成 pyodbc.Cursor object 并转成list
        cursor_list = [x for x in self.cursor.execute(hold_table)]
        print('开始更新持仓...')
        for item in cursor_list:
            # 获取code和名称
            x = item.code
            name = item.名称
            # 从tushare获取价格

            # k_data = ts.get_k_data(x,start=start_date,end=latest_day)
            df = ts.get_realtime_quotes(x)
            # 判断是否为空
            if df.empty is False:
                price = df[['price']].iloc[0,0]
                price2 = float(price)
                # access要求写入数据必须为字符串
                if price2 >0.05:
                    price = str(price)
                    print(name,price)
                    # 将代码和价格更新到对应的股票中
                    self.cursor.execute("UPDATE buy SET 即时价 = '"+ price +"' WHERE code= '"+ x +"'")
                    self.cursor.commit()
            # print(name)

    def updateHistory(self):

        history_table = "SELECT code,名称 FROM 按名称利润表"
        # 将查询语句执行生成 pyodbc.Cursor object 并转成list
        history_list = [x for x in self.cursor.execute(history_table)]
        print('开始更新历史...')
        for item in history_list:
            # 获取code和名称
            x = item.code
            name = item.名称
            # 从tushare获取价格

            # k_data = ts.get_k_data(x,start=start_date,end=latest_day)
            df = ts.get_realtime_quotes(x)
            # 判断是否为空
            if df.empty is False:
                price = df[['price']].iloc[0,0]
                price2 = float(price)
                # access要求写入数据必须为字符串
                if price2 >0.05:
                    price = str(price)
                    # 查询是否table已经有这个记录了
                    price_table = "SELECT * FROM 历史单当前股价 WHERE code = '"+ x +"'"
                    price_list = [x for x in self.cursor.execute(price_table)]
                    #如果已经存在记录，则更更新价格
                    if len(price_list) >0:
                        self.cursor.execute("UPDATE 历史单当前股价 SET price = '"+ price +"',名称 = '"+ name +"' where code= '"+ x +"'")
                        print('更新价格...',name,price)
                        self.cursor.commit()
                    else:
                        self.cursor.execute("INSERT INTO 历史单当前股价(code,名称,price) VALUES( '" + x + "','"+ name +"','" + price + "')")
                        print('新增记录...', name,price)
                        self.cursor.commit()
            else:
                print('没有价格信息',name)
        self.cursor.close()
        print('更新完成！')

if __name__ == "__main__":
    run = updatePrice()