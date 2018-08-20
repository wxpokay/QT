# -*- coding: utf-8 -*-
# @Time    : 17/12/14 上午10:39
# @Author  : ritawu

from ws4py.client.threadedclient import WebSocketClient
import json
import time
import _thread


class DummyClient(WebSocketClient):
    listeners = {
        'connected': [],
        'receiveHeart': []
    }  # 仿 js 的，作用未知
    unsend = []  # 未发送数据
    connected = False
    live = False
    seq = 0  # 步数，用于验证数据是否完整
    reconn = False
    last_time = time.time()
    ids = ''
    account = ''
    orderid = ''
    price = 0
    oldst = ''

    def opened(self):  # 发送连接包，与服务器连接，否则服务器会断开连接
        data = {
            'p_no': 1,
            'p_ver': 1,
            'p': {
                'pt': 1,
                'seq': self.seq + 1,
                'clientid': 'SupportTT',
                'appid': 'WebSock',
                'ver': '1.0',
                # 'id': 'AAPL.US.SC',
                # 'fs': 1,
                # 'ch': 1
            }

        }
        self.seq = self.seq + 1
        self.send(json.dumps(data))

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, m):  # 这是回调函数，当有信息传递进来的时候就会被调用
        self.last_time = time.time()
        m.encoding = "utf-8"
        self.reconn = False
        try:
            obj = json.loads(m.__str__())
            li = obj["L"]
            for i in li:
                self.swi(i["p"])
        except:
            print("未被decode的包")
            pass

    def swi(self, st):  # 根据 pt 对返回的信息进行分类
        pt = st["pt"]
        if pt == 2:
            self._handle_connect_challenge(st)  # 这是由服务器传递回来的，以确认是真的客户端发送的连接请求
        elif pt == 9:
            self._error_status(st)
        elif pt == 301:
            self._handle_market_status_update(st)  # 这是验证市场
        elif pt == 4:
            self._handle_connect_status()  # 表明服务器验证已经通过
        elif pt == 6:
            self._handle_receive_alive(st)  # 这个是心跳连接
        elif pt == 302:
            self._handle_quote_update(st)  # 这个是订阅返回数据
        elif pt == 901:
            self._handle_connect_status()
        elif pt == 101:
            self._subscriber_status(st)  # 这个是说明订阅错误
        elif pt == 306:
            self._user_login_status(st)
        elif pt == 304:
            self._order_update_status(st)

    # 委託單類別：0為Update，1為Enter，2為Amend，3為Cancel，4為StopLoss，5為Get (回應 GetOrder)
    def _order_update_status(self, st):
        if str(st).__contains__("err"):
            print("委托失败:" + str(st['d']))
        if st['d'][0]['type'] == 1 and st['d'][0]['ostatus'] == 0:
            self.oldst = st
            self.orderid = str(st['d'][0]['id'])
            print(st['d'][0]['id'], "委托成功但未成交")
        if st['d'][0]['ostatus'] == 2 and (st['d'][0]['ostatus'] != self.oldst['d'][0]['ostatus']) and st['d'][0][
            'side'] == 1:
            self.oldst = st
            print(st['d'][0]['id'], "买入委托单全部成交")
        if st['d'][0]['ostatus'] == 2 and (st['d'][0]['ostatus'] != self.oldst['d'][0]['ostatus']) and st['d'][0][
            'side'] == 2:
            self.oldst = st
            print(st['d'][0]['id'], "卖出委托单全部成交")
        if st['d'][0]['ostatus'] == 1:
            print("委托单部分成交")
        if st['d'][0]['type'] == 2:
            print(st['d'][0]['id'], "修改委托成功")
        if st['d'][0]['type'] == 3:
            print(st['d'][0]['id'], "撤单成功")

    def _error_status(self, st):
        print("错误:", str(st["msg"]))

    def _user_login_status(self, st):
        self.ids = st["user"]
        self.account = st["def"]
        print(self.ids, "登录成功")

    def _subscriber_status(self, st):  # 订阅的时候返回的错误信息
        if st.__contains__("err"):
            print("订阅的错误信息为：" + str(st["msg"]))

    def _handle_quote_update(self, st):
        self.fire("quoteUpdate", st)

    def _handle_receive_alive(self, st):  # 这是说明联机正常
        self.fire("receiveHeart", st)

    def _handle_timeout(self, ti):
        while True:
            time.sleep(ti)
            if self.connected:
                self.connected = False
                return
            if self.reconn:
                time.sleep(10)
                if self.reconn:
                    self.reconnect()

    def reconnect(self):
        self.connected = True
        self.live = True
        print("重新连接")
        time.sleep(18)
        wc = DummyClient(url=self.url)
        wc.unsend = self.unsend
        self.connect()
        print("连接成功")

    def _handle_connect_status(self):  # 这是只发送一次的数据，所以在这里创建监听线程
        self.reconn = True  # 需要重连
        if len(self.unsend) != 0:
            for option in self.unsend:  # 当连接的时候看是否有未发送的数据，有的话就发送
                self.send(option)
        _thread.start_new_thread(self._handle_alive, (5,))  # 连接成功就要保持连接，定时向服务器发送心跳包
        _thread.start_new_thread(self._handle_timeout, (15,))  # 这个是监听连接状态的线程，如果未连接，就重连

    def _handle_alive(self, sleep_time):  # 创建一个单独的线程，与服务器进行心跳连接
        while True:  # 在发送心跳包的时候就检测一下，如果是已经重连过了，就退出，结束线程，有可能会存在两个心跳线程同时存在的情况，
            time.sleep(sleep_time)  # 如果连接结束后重连，那么原来的心跳线程就需要退出，那么就在重连后将标志位置为 true
            if self.live:
                self.live = False
                return
            spkt = {
                'p_no': 1,
                'p_ver': 1,
                'p': {
                    'pt': 5,
                    'seq': self.seq + 1
                }
            }
            self.reconn = True
            self.seq += 1
            self.send(json.dumps(spkt))

    def _handle_connect_challenge(self, st):  # 其中 r 是服务器发送来的密文要求 client 使用自己的 RSA private key 加密此亂數，用以驗證此 Client 是否為真。
        rpkt = {  # 这是回应服务器发送来的加密验证数据
            'p_no': 1,
            'p_ver': 1,
            'p': {
                'pt': 3,
                'seq': self.seq + 1,
                'r': st["r"],
                'country': 'TW',
                'lang_code': 'TW'
            }
        }
        self.seq += 1
        self.send(json.dumps(rpkt))

    def _handle_market_status_update(self, st):
        self.fire('marketStatusUpdate', st)

    def fire(self, event, args):  # 这是是仿 js 的，作用未知
        if not self.listeners.__contains__(event):
            return False
        else:
            ite = self.listeners.get(event)
            for fn in ite:
                fn and fn(args)

    def subscribe_quote(self, ide):  # 订阅信息
        data = {
            'p_no': 1,
            'p_ver': 1,
            'p': {
                'pt': 102,
                'seq': self.seq + 1,
                'id': ide,
                'fs': 4,
                'ch': 4
            }
        }
        self.seq += 1
        print(json.dumps(data))
        self.unsend.append(json.dumps(data))
        self.send(json.dumps(data))

    def user_login(self, ids, passwd):
        data = {
            "p_no": 1,
            "p_ver": 1,
            "p": {
                "pt": 209,
                "seq": self.seq + 1,
                "user": ids,
                "pwd": passwd,
                "parseid": "",
                "country": "CN",
                "lang_code": "CN",
                "login_type": 0
            }
        }
        self.seq += 1
        time.sleep(2)
        self.unsend.append(json.dumps(data))
        self.send(json.dumps(data))

    def limit_order(self, sym, side, price, qty):

        data = {
            "p_no": 1,
            "p_ver": 1,
            "p": {
                "pt": 203,
                "seq": self.seq + 1,
                "account": self.account,
                "sym": sym,
                "side": side,
                "otype": 2,
                "price": price,
                "qty": qty,
                "strategy": 1,
                "reason": 0,
                "txid": 'enterOrder_' + str(self.seq),
                "user": self.ids
            }
        }
        self.seq += 1
        time.sleep(2)
        self.unsend.append(json.dumps(data))
        self.send(json.dumps(data))

    def market_order(self, sym, side, qty):
        data = {
            "p_no": 1,
            "p_ver": 1,
            "p": {"otype": 1,
                  "pt": 203,
                  "seq": self.seq + 1,
                  "account": self.account,
                  "sym": sym,
                  "side": side,
                  "qty": qty,
                  "strategy": 1,
                  "reason": 0,
                  "txid": 'enterOrder_' + str(self.seq),
                  "user": self.ids
                  }
        }
        self.seq += 1
        time.sleep(2)
        self.unsend.append(json.dumps(data))
        self.send(json.dumps(data))

    def amend_order(self, price, qty):
        data = {
            "p_no": 1,
            "p_ver": 1,
            "p": {
                "pt": 204,
                "seq": self.seq + 1,
                "account": self.account,
                "id": self.orderid,
                "user": self.ids,
                "txid": 'amendOrder_' + str(self.seq),
                "price": price,
                "qty": qty
            }
        }
        self.seq += 1
        time.sleep(2)
        self.unsend.append(json.dumps(data))
        self.send(json.dumps(data))

    def cancel_order(self):
        data = {
            "p_no": 1,
            "p_ver": 1,
            "p": {
                "pt": 205,
                "seq": self.seq + 1,
                "account": self.account,
                "id": self.orderid,
                "user": self.ids,
                "txid": "cancelOrder" + str(self.seq)
            }
        }
        self.seq += 1
        time.sleep(2)
        self.unsend.append(json.dumps(data))
        self.send(json.dumps(data))

    def disconnect(self):  # 关闭连接,发送关闭包后服务端会自动断开连接
        option = {
            'p_no': 1,
            'p_ver': 1,
            'p': {
                'pt': 7
            }
        }
        self.send(json.dumps(option))
        print("连接已经关闭")
