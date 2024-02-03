# Author: Nike Liu
import sys
sys.path.append('..')
import tushare as ts
from util.database import conn
print('开始更新...')

# 从tushare获取股票基本信息
df = ts.get_stock_basics()
df = df.reset_index()[['code','name']]

cursor = conn.cursor()
# 判断是否为空
if df.empty is False:
    # 从access中提取持仓股(code为空)的list
    hold_table = "SELECT * FROM buy where code is null"
    # 将查询语句执行生成 pyodbc.Cursor object 并转成list
    cursor_list = [x for x in cursor.execute(hold_table)]
    for item in cursor_list:
        # 获取code和名称
        name = item.名称

        code_list = df.loc[(df["name"] == name)]['code'].tolist()
        # code = new_df.iloc[0,0]
        if len(code_list) >0:  # 没有这个判断会错，因为list可能为空。
            code = code_list[0]
            # access要求写入数据必须为字符串
            cursor.execute("UPDATE buy SET code= '"+ code +"' WHERE 名称 = '"+ name+"'")
            print(name, code)
            cursor.commit()
    # print(name)
cursor.close()
print('更新完成！')