import sqlite3,pyodbc
import os
# 获取当前路径
path = os.getcwd()

if 'util' in path:
    path = path.replace("\\util","")
print(path)
# SQLite db 数据库
db_file = path + '\db\stock_record.db'
DB_CONN = sqlite3.connect(db_file) #如果路径里面没有这个数据库，会自动创建
# print(path)
# Access db 数据库
odbc_file = path + '\db\stock_records.accdb'  # 存放股票的数据库文件
conn = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + odbc_file + ";Uid=;Pwd=ll;")

# Pharmasi access 数据库
# chemical_db_path = r'Z:\db\20120815.accdb'  # 存放chemical 订单的数据库文件
# chemical_db = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + chemical_db_path + ";Uid=;Pwd=jh2005;")
