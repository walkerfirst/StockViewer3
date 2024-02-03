# Author: Nike Liu
"""
将交易记录存在.xlsx文件中，并分买单和卖单分类存到access对应的表中
注意：文件后缀必须为.xlsx，而且需要另存为，直接改后缀名可能无效。
买单添加测试ok
卖单1对1添加测试ok
分批卖出测试ok
1卖单对应多个买单测试ok
"""
import sys
sys.path.append('..')
from util.database import conn
import pandas as pd
from datetime import datetime
from setting.account import Account
from DataEngine import DataEngine


class ProcessTrading(object):
    def __init__(self,data):
        self.data = data
        self.cursor = conn.cursor()
        self.date = self.data['date']
        self.code = str(self.data['code'])
        # 对代码补齐
        if len(self.code) < 6:
            self.code = self.code.rjust(6, '0')
        self.name = self.data['name']
        # 买的时候是发债，卖的时候是转债。为了统一而改名字。
        # if self.name.find('发债') >= 0:
        #     self.name = self.name.replace("发债", "转债")
        self.qty = self.data['qty']
        self.str_qty = str(self.qty)
        self.price = self.data['price']
        self.str_price = str(self.price)
        self.stop = str(self.price*0.9)
        self.fei = str(self.data['fei'])
        self.tax = str(self.data['tax'])
        self.account = self.data['account']
        self.option = self.data['option']

        # acc_sql = "SELECT cash,实现盈利 from 账户 WHERE code='" + self.account + "'"
        # acc_list = [x for x in self.cursor.execute(acc_sql)]
        # # print(acc_list)
        # self.profit = acc_list[0].实现盈利
        # self.cash = acc_list[0].cash
        self.accDict = DataEngine().accDict[self.account]
        self.profit = self.accDict['profit']
        self.cash = self.accDict['cash']

    def updateCash(self):
        # 将data（list）更新到账户表中
        # print(self.name)
        if '买入' in self.option:
            new_cash = self.cash - float(self.fei) - self.price * self.qty
        elif "债" in self.name:
            new_cash = self.cash - float(self.fei) - float(self.tax) + self.data['amount']
            # print(new_cash)
        else:
            new_cash = self.cash - float(self.fei) - float(self.tax) + self.price * self.qty
        if new_cash >= 0:
            self.cursor.execute("UPDATE 账户 SET cash = '" + str(new_cash) + "' WHERE code= '" + self.account + "'")
            self.cursor.commit()
        else:
            print('现金不够了')

    def updateProfit(self,buy_price):
        # 将data（list）更新到账户表中

        new_profit = self.profit + self.qty * (self.price -buy_price) - float(self.fei) - float(self.tax)
        new_profit_str = str(new_profit)
        self.cursor.execute("UPDATE 账户 SET 实现盈利 = '" + new_profit_str + "' WHERE code='" + self.account + "'")
        self.cursor.commit()

    # 插入买入数据到access
    def buy_ation(self):

        sql = "INSERT INTO buy(买入日期,code,名称, 数量,买入价,即时价,止损,佣金,account) VALUES('"+self.date+"','"+self.code+"'," \
         "'"+self.name+"', '"+self.str_qty+"', '"+self.str_price+"', '"+self.str_price+"', '"+self.stop+"', '"+self.fei+"', '"+self.account+"')"
        self.cursor.execute(sql)
         # 提交数据（只有提交之后，所有的操作才会生效）
        # 跟新现金
        self.updateCash()
        self.cursor.commit()

    # 插入卖出数据到access
    def sell_ation(self):

        # 先把卖单的cash更新到数据库
        self.updateCash()
        # 获取买单信息
        sql_hold = "SELECT * FROM 持仓 WHERE code = '"+self.code+"' AND account = '"+self.account+"' "
        # 将查询语句执行生成 pyodbc.Cursor object 并转成list
        hold_df = DataEngine().dbQurey(sql=sql_hold)
        # 按照买入日期和数量重新排序
        hold_df = hold_df.sort_values(by=['买入日期','数量'],ascending=[False,True])
        if not hold_df.empty:
            select_df = hold_df[hold_df['数量'] == self.qty]
            # 买单中有记录和卖出数量正好一致
            if not select_df.empty:
                # 优先卖出有卖出记录的买单
                select_df2 = hold_df[hold_df['qty'] == self.qty]
                if not select_df2.empty:
                    buy_ID = select_df2.iloc[0]['ID']
                    buy_price = select_df2.iloc[0]['买入价']
                else:
                    # 如果没有卖出的买单，取最近的一条买单记录
                    select_series = select_df.iloc[0]
                    buy_ID = select_df.iloc[0]['ID']
                    buy_price = select_df.iloc[0]['买入价']
                buy_ID = str(buy_ID)
                # print('= =',buy_ID,buy_price)
                # 更新利润
                self.updateProfit(buy_price)

            #     # 插入一条卖出数据
                insert_sql = "INSERT INTO sale(卖出日期,名称, 数量,卖出价,ID,佣金,税金,code) VALUES ('" + self.date + "',"\
                "'" + self.name + "', '" + self.str_qty + "', '" + self.str_price + "', '" + buy_ID + "', '" + self.fei + "'," \
                    " '" + self.tax + "', '" + self.code + "')"
                self.cursor.execute(insert_sql)
            #     # 买单结单
                self.cursor.execute("UPDATE buy SET 结单 = 'Y' WHERE ID =" + buy_ID)
                self.cursor.commit()  # 提交数据（只有提交之后，所有的操作才会生效）

            # 对于卖出数量与买入数量不同情况
            else:
                qty_min = hold_df['数量'].min()

                # 部分卖出情况
                if self.qty < qty_min:
                    # 优先处理有卖出记录的买单
                    select_df3 = hold_df[hold_df['qty'] > 0]
                    # 查看卖单是否有部分卖出情况
                    if not select_df3.empty:
                        buy_ID = select_df3.iloc[0]['ID']
                        buy_price = select_df3.iloc[0]['买入价']
                    else:
                        buy_ID = hold_df.iloc[0]['ID']
                        buy_price = hold_df.iloc[0]['买入价']

                    # print('min',buy_ID,buy_price)
                    # 更新利润
                    self.updateProfit(buy_price)

                    insert_sql = "INSERT INTO sale(卖出日期,名称, 数量,卖出价,ID,佣金,税金,code) VALUES ('" + self.date + "'" \
                   ",'" + self.name + "', '" + self.str_qty + "', '" + self.str_price + "', '" + str(buy_ID) + "', '" + self.fei + "'," \
                        " '" + self.tax + "', '" + self.code + "')"
                    self.cursor.execute(insert_sql)
                    self.cursor.commit()

                # 单次卖出多个买单的情况
                elif self.qty > qty_min:
                    buy_cost = 0  # 买入成本
                    buy_qty_total = 0  # 本次累计卖出数量
                    remain_buy_qty = 0  # 本次之前剩余卖出数量
                    for i in range(0,hold_df.index.size):
                        remain_buy_qty = self.qty - buy_qty_total
                        buy_series = hold_df.iloc[i]
                        buy_ID = str(buy_series['ID'])
                        buy_qty = buy_series['数量']
                        buy_qty_str = str(buy_qty)
                        buy_qty_total += buy_qty

                        # 若剩余数量小于买单数量，视为部分卖出
                        if remain_buy_qty < buy_qty:
                            buy_qty = remain_buy_qty
                            buy_qty_str = str(buy_qty)
                        buy_value = buy_series['买入价'] * buy_qty
                        buy_cost += buy_value

                        # print(buy_qty,buy_ID)

                        fei = str(round(self.data['fei'] * buy_qty / self.qty,2))
                        tax = str(round(self.data['tax'] * buy_qty / self.qty,2))
                        insert_sql= "INSERT INTO sale(卖出日期,名称, 数量,卖出价,ID,佣金,税金,code) VALUES ('" + self.date + "'," \
                         "'" + self.name + "', '" + buy_qty_str + "', '" + self.str_price + "', '" + buy_ID + "', '" + fei + "'," \
                            " '" + tax + "', '" + self.code + "')"
                        self.cursor.execute(insert_sql)
                        # 买单结单
                        if remain_buy_qty >= buy_series['数量']:  # 注意：此时buy_qty != buy_series['数量']
                            # print('结单',remain_buy_qty,buy_ID)
                            self.cursor.execute("UPDATE buy SET 结单 = 'Y' WHERE ID =" + buy_ID)
                            self.cursor.commit()  # 提交数据（只有提交之后，所有的操作才会生效）
                        if buy_qty_total >= self.qty:
                            # print('执行退出', remain_buy_qty, buy_ID)
                            break
                    # 计算平均价格
                    avg_buy_price = round(buy_cost/self.qty,2)
                    print(avg_buy_price)
                    # 更新利润
                    self.updateProfit(avg_buy_price)

            # self.cursor.close()
    # 插入买入数据到access
    def ZX_ation(self):
        """新股中签卖出处理"""
        amount = str(self.data['amount'])
        self.cursor.execute("INSERT INTO 福利(code,name, amount,dates,model,account) VALUES('"+self.code+"','"+self.name+"', "
                                "'"+amount+"', '"+self.date+"', '中新','"+self.account+"')")
        self.cursor.execute("UPDATE buy SET 结单 = 'Y' WHERE code ='"+self.code+"'")
        self.cursor.commit() # 提交数据（只有提交之后，所有的操作才会生效）
        self.updateCash()
        # self.cursor.close()

    def hongli_ation(self):
        """现金分红处理"""
        amount = str(self.data['amount'])
        if "债" in self.name:
            fenlei = '中新'
        else:
            fenlei = '分红'
        self.cursor.execute("INSERT INTO 福利(code,name, amount,dates,model,account) VALUES('"+self.code+"','"+self.name+"', "
                                    "'"+amount+"', '"+self.date+"', '"+fenlei+"','"+self.account+"')")
        self.cursor.commit() # 提交数据（只有提交之后，所有的操作才会生效）

class update_records_to_access(object):
    def __init__(self):
        # excel文件存放目录
        file_path = '../data/table.xlsx'
        df = pd.read_excel(file_path)

        if "佣金" in df.columns:
            df.rename(columns={'佣金': '手续费'}, inplace=True)
        # 按照成交日期正向排序
        df = df.sort_values(by=['成交日期','成交时间'], ascending=True)
        df = df[['成交日期', '证券代码','证券名称', '操作', '成交数量', '成交均价', '手续费', '印花税', '成交金额','股东帐户']]
        table = df[df['操作'].str.contains("买入|卖出|红股入账")]  # 筛选出买入卖出的操作

        # 数量取绝对值，防止负数
        table.rename(columns={'成交日期': 'date', '证券代码':'code', '证券名称':'name','操作':'option',
                              '成交数量':'qty', '成交均价':'price','手续费':'fei', '印花税':'tax',
                              '成交金额':'amount', '股东帐户':'account'}, inplace=True)
        # 重置索引，不然会出错
        table = table.reset_index(drop=True)

        # 账户id转换，把交易所的账号对应
        for index in table.index:
            trade_account = table.iloc[index]['account']
            for key in Account.keys():
                if trade_account in list(Account[key].values()):
                    table.loc[index, 'account'] = key

            table.loc[index,'qty'] = abs(table.iloc[index]['qty'])
            # 把日期转成str并改变样式
            date = table.iloc[index]['date']
            date_strp = datetime.strptime(str(date),'%Y%m%d')
            date_strf = date_strp.strftime('%Y-%m-%d')
            table.loc[index, 'date'] = date_strf

            data = table.iloc[index]
            # print(data)

            if "买入" in data['option']:
                ProcessTrading(data).buy_ation()
            elif '卖出' in data['操作']:
                ProcessTrading(data).sell_ation()
            elif '红股入账' in data['操作']:
                ProcessTrading(data).hongli_ation()

if __name__ == '__main__':
    update_records_to_access()

# 下面是测试
# cursor = conn.cursor()
# SQL = "SELECT * FROM sale WHERE 编号 >= 300;"
# for row in cursor.execute(SQL):
#     print(row)
#
# cursor.commit() # 提交数据（只有提交之后，所有的操作才会生效）
# cursor.close()
# conn.close()

