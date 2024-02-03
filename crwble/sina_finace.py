"""
从新浪网上下载财务数据
"""
import requests
import pandas as pd
from pandas import DataFrame
import time

headers = {
          "user-agent": "Mozilla/5.0 (windows NT 10.0; WoW64)" "AppLeWebKit/537.36 (KHTML, like Gecko) Chrome/ 75. 0.3770.100 Safari/537.36"
    }

def get_stockList(file_path):
    df = pd.read_excel(file_path)
    stock_list = list(df['code'])
    return stock_list
def get_balanceSheet(stock_id_list,year_list):
    for i in stock_id_list:
        for j in year_list:
            url = 'https://money.finance.sina.com.cn/corp/go.php/' \
                  'vFD_CashFlow/stockid/%s/ctrl/%s/displaytype/4.phtml' % (i,j)
            # print(url)
            time.sleep(3)
            try:
                response = requests.get(url=url,headers=headers)
                data = pd.read_html(response.text)[13]
                df = DataFrame(data)
                df.to_excel("E:\\project\\StockViewer_v3.0\\crwble\\data\\"+str(i)+str(j)+'cashFlow.xlsx', index = False)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    yearlist = [2020,2021]
    stock_list = ['601318','601058']
    get_balanceSheet(stock_list,yearlist)

