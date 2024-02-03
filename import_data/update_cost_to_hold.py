# Author: Nike Liu

""" 针对分红或者送股情况，对持仓股票进行除权，重新调整单位成本"""
import sys
sys.path.append('..')
import tushare as ts
from util.database import conn
from util.latest_tradeday import start_date,latest_day
print('开始更新...')
# 从access中提取持仓股的list
cursor = conn.cursor()
name = '天山股份'
change_rate = 12.49/13
hold_table = "SELECT * FROM buy where 结单 = 'N' and 名称 = '" + name + "'"
# 将查询语句执行生成 pyodbc.Cursor object 并转成list
cursor_list = [x for x in cursor.execute(hold_table)]

for item in cursor_list:
    # 获取ID和名称
    id = str(item.ID)
    cost = item.买入价
    new_price = round(cost*change_rate,2)
    price = str(new_price)
    print(id,price)

    # 将代码和价格更新到对应的股票中
    cursor.execute("UPDATE buy SET 买入价 = '"+ price +"' WHERE ID = +id ")
    cursor.commit()
    # print(name)

cursor.close()
print('更新完成！')