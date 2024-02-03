# Author: Nike Liu
import pandas as pd


import sqlite3
"""把excel数据转存到sqlite数据中"""
df = pd.read_excel(r'../db/sell.xlsx',encoding='gbk')
# 分列后，再把新的列赋值给原来的code，此项的目的是防止code前面的0被消灭
df['code'] = df['code'].str.split('.',expand = True)[1]
# df['code'] = df['code'].apply(str)
# print(df[['code','name']].head(100))

db = sqlite3.connect('../db/stock_record.db') #如果路径里面没有这个数据库，会自动创建

df.to_sql(name='sell',con=cx,if_exists='append',index=True)

# 设置sql筛选语句
sql = "select * from sell"

test = pd.read_sql(sql,db) #完成数据库的查询读取到dataframe 中
# print(test.tail(5))

"""
to_sql
参见pandas.to_sql函数，主要有以下几个参数：

name: 输出的表名
con: 与read_sql中相同
if_exits： 三个模式：fail，若表存在，则不输出；
                    replace：若表存在，覆盖原来表里的数据；
                    append：若表存在，将数据写到原表的后面。默认为fail

index：是否将df的index单独写到一列中
index_label:指定列作为df的index输出，此时index为True
chunksize： 同read_sql
dtype: 指定列的输出到数据库中的数据类型。字典形式储存：{column_name: sql_dtype}。常见的数据类型有sqlalchemy.types.INTEGER(), sqlalchemy.types.NVARCHAR(),sqlalchemy.Datetime()等，具体数据类型可以参考这里
还是以写到mysql数据库为例：
df.to_sql(name='table', 
          con=con, 
          if_exists='append', 
          index=False,
          dtype={'col1':sqlalchemy.types.INTEGER(),
                 'col2':sqlalchemy.types.NVARCHAR(length=255),
                 'col_time':sqlalchemy.DateTime(),
                 'col_bool':sqlalchemy.types.Boolean
          })
"""

