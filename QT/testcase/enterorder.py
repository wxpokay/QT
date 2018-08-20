#-*- coding: UTF-8 -*-
# @Time    : 17/12/19 下午12:23
# @Author  : ritawu

import time
from ltsapi import DummyClient


class EnterOrder():
    def runTest(self):
        username = "ritatest"
        passwd = "123456"
        sym = "00700.HK.SC"
        #======================
        print("\ncase 1. 登录交易员账号\n")
        #======================
        ws = DummyClient('wss://tradetest.investmaster.cn:443')  # 超时93s，自动断开
        va = ws.connect()
        time.sleep(2)
        print("即将登录", username, passwd)
        ws.user_login(username, passwd)
        time.sleep(2)

        #======================
        print("\ncase 2. 限价买入100股委托成功,但未成交\n")
        #======================
        ws.limit_order(sym, 1, 10, 100)
        time.sleep(5)

        #======================
        print("\ncase 3. 取消委托单\n")
        #======================
        ws.cancel_order()
        time.sleep(3)

        #======================
        print("\ncase 4. 限价买入100股委托成功,且成交\n")
        #======================
        ws.limit_order(sym, 1, 500,100)
        time.sleep(3)

        # ======================
        print("\ncase 5. 限价卖出100股委托成功,且成交\n")
        # ======================
        ws.limit_order(sym, 2, 2,100)
        time.sleep(3)

        # ======================
        print("\ncase 6. 修改委托单\n")
        # ======================
        ws.limit_order(sym, 1, 10, 100)
        time.sleep(3)
        ws.amend_order(50,200)
        time.sleep(3)

        # ======================
        print("\ncase 7. A股无法进行市价单买卖\n")
        # ======================
        ws.market_order("000088.SZ.SC",1,100)



        ws.run_forever()



if __name__ == '__main__':
    try:
        EnterOrder().runTest()
    except  KeyboardInterrupt as e:
        print(e)
