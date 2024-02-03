# Author: Nike Liu
from util.database import conn
cursor = conn.cursor()
# 删除表
# cursor.execute("DROP TABLE 分红")
# 新建表，并设置id为自动编号
# sql = "CREATE TABLE 新股(id AUTOINCREMENT(1,1),code varchar(20),name varchar(20),amount double,dates varchar(20))"
# cursor.execute(sql)
# 给表添加数据
# add_data = "INSERT INTO 分红(code,name,amount,dates) VALUES('123050','聚飞转债',211,'2020-05-18')"
cursor.execute("DELETE FROM buy WHERE 名称 like '%北鼎股份%'")
# cursor.execute(add_data)
# 清空表中数据
# cursor.execute("delete * from 分红")
cursor.commit()

fh_table = "SELECT * FROM 福利"
# 将查询语句执行生成 pyodbc.Cursor object 并转成list
cursor_list = [x for x in cursor.execute(fh_table)]

print(cursor_list)