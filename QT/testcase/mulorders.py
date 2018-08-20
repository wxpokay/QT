#-*- coding: UTF-8 -*-
# @Time    : 17/12/14 上午10:40
# @Author  : ritawu

import time
from ltsapi import DummyClient
import csv
import multiprocessing

#交易账号列表,route均被设置为 fdt01,dtuser.csv 为股票池账号, user.csv 为普通账号
path = '../file/dtuser.csv'

#交易次数
trade_count = 10

#买入价格,建议将买入价格设置成低于最新价,如果 route 为非 fdt01 的交易账号,则价格设置相反,以便成交
buy_price = 50

#卖出价格,建议将卖出价格设置成高于最新价,如果 route 为非 fdt01 的交易账号,则价格设置相反,以便成交
sell_price = 60

#买入的数量
buy_count = 100

#卖出数量
sell_count = 100

#交易 symbol 设置,如果为股票池账户,则需要设置为股票池里 symbol
sym = '000088.SZ.SC'

def limitBuy(sym, username, passwd):
    try:
        ws = DummyClient('wss://tradetest.investmaster.cn:443')  # 超时93s，自动断开
        va = ws.connect()
        time.sleep(2)
        print("即将登录", username, passwd)
        ws.user_login(username, passwd)
        time.sleep(2)
        global trade_count, buy_price, sell_price, buy_count, sell_count
        for i in range(trade_count):
            ws.limit_order(sym, 1, buy_price, buy_count)  # 限价买入
            time.sleep(0.4)
        for i in range(trade_count):
            ws.limit_order(sym, 2, sell_price, sell_count)  # 限价卖出
            time.sleep(0.4)
        ws.run_forever()
    except KeyboardInterrupt as e:
        print(e)

def loginUser():
    try:
        with open(path,'r') as csvfile:
            reader = csv.DictReader(csvfile)
            traderlist = []
            trader = []
            for row in reader:
                traderlist.append(row)
            return traderlist
    finally:
        if csvfile:
            csvfile.close()

class PressEnterOrder():
    def runTest(self):
        trader = loginUser()
        try:
            process = []
            for i in range(len(trader)):
                p = multiprocessing.Process(target=limitBuy,
                                            args=(sym, trader[i]['username'], trader[i]['password'],))
                process.append(p)
            for pro in process:
                pro.start()
                time.sleep(2)
        except KeyboardInterrupt as e:
            print(e)




if __name__ == '__main__':
    PressEnterOrder().runTest()

