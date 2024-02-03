# Author: Nike Liu
import sys
sys.path.append('..')
from util.database import conn
print('开始更新...')
cursor = conn.cursor()
# 从access中提取持仓股(code为空)的list
hold_table = "SELECT code,名称 FROM buy"
# 将查询语句执行生成 pyodbc.Cursor object 并转成list
cursor_list = [x for x in cursor.execute(hold_table)]
for item in cursor_list:
    # 获取code和名称
    name = item.名称
    code = item.code
    # access要求写入数据必须为字符串
    cursor.execute("UPDATE sale SET code= '"+ code +"' WHERE 名称 = '"+ name+"'")
    print(name, code)
    cursor.commit()
# print(name)

cursor.close()
print('更新完成！')