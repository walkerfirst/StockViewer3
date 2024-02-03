from util.database import DB_CONN
import pandas as pd

class DatabaseTools(object):
    """database 的操作类"""
    def __init__(self,tablename):
        self.table = tablename
        self.db = DB_CONN
        self.cursor = self.db.cursor()

    def execute_sql(self,sql):
        self.cursor.execute(sql)
        self.db.commit()
        self.db.close()

    def get_tables(self):
        sql_all_tables = "SELECT name FROM sqlite_master WHERE type='table';"
        self.cursor.execute(sql_all_tables)
        tables = self.cursor.fetchall()
        table_list = []
        for i in tables:
            table_list.append(i[0])
        return table_list

    def if_table_exit(self):
        table_list = self.get_tables()
        if self.table in table_list:
            return True
        else:
            return False

    def clear_table(self):
        if self.if_table_exit():
            sql_clear = "delete from '"+self.table+"'"
            self.execute_sql(sql_clear)
            print('table delt is done')
        else:
            print('table is not exited')

    def create_table(self):
        if not self.if_table_exit():
            sql_add = "create table '"+self.table+"'('index' INTEGER PRIMARY KEY,'buy_id' INTEGER,'buy_date'TIMESTAMP,'code' TEXT,'name' TEXT,buy_price REAL," \
                "closed REAL,'account' TEXT,'buy_qty' INTEGER,'buy_reason' TEXT,'fees' REAL, 'is_completed' TEXT,'stop' REAL);"
            self.execute_sql(sql_add)
            print('table creation is done')
        else:
            print('table is already exited')

    def add_columns(self):
        sql_add = "ALTER TABLE '"+self.table+"' ADD fees TREL"
        self.execute_sql(sql_add)

    def del_table(self):
        sql_del = "drop table '"+self.table+"'"
        if self.if_table_exit():
            sql_clear = "delete from '" + self.table + "'"
            self.execute_sql(sql_del)
            print('table delt is done')
        else:
            print('table is not exited')

    def read_db(self,sql):
        df = pd.read_sql(sql, self.db)
        return df
if __name__ == '__main__':
    table = 'sell'
    sql = 'select * from sale where ID = 38'
    run = DatabaseTools(table).read_db(sql)
    print(run)
