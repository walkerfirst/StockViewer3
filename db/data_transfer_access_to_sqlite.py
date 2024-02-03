from util.access_db import read_access_db
import pandas as pd
from util.database import DB_CONN
# 从access 中读取buy表数据，并转换成dataframe
sql_buy = 'select * from sale'
data = read_access_db(sql_buy)

# 从access 中读取buy表数据，并转换成dataframe
# sql_sell = 'select * from sale'
# data = read_access_db(sql_sell,column_list=['index','sell_date','name','sell_price','sell_qty','buy_id','fees','tax','code'])

print(data.tail(10))

# 将数据存入sqlite数据库中
data.to_sql('sale',con=DB_CONN,if_exists='append',index=False)

# 从sqlite读取数据,只取10条
# sql = "select * from buy limit 0,10"

# test = pd.read_sql(sql,DB_CONN)#完成数据库的查询读取到数据框dataframe 中
# print(test.tail(12))