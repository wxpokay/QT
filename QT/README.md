# 相关库的安装
    使用 Python 3.0 以上版本
1. 需要的库
   需要 ws4py
安装说明
    1, 使用 PyCharm 安装
        点击顶栏中的 (PyCharm Community Edition ), 在下拉列表中选中 Preferences 进入配置页面
        找到 Project:python( python 是当前项目的名字), 点击,之后找到 Project:Interpreter 并点击
        在 Project:Interpreter 一栏显示的是 python 的版本, 请确定是 3.0 及以上
        在显示 Package, Version, Latest 一栏中, 找到 + 或者 add 按钮
        进入添加库界面
        在搜索框数据没有添加的库的名字, 选中之后点击下方的 Install Package
        安装成功后会提示 Package .. installed successfully
        如果因为网络原因安装失败, 就点击 Manage Repositories
        在弹出的界面中点击 + 或者 add, 在输入框中输入下列地址
        https://pypi.douban.com/simple/ (国内镜像地址)
        点击 ok 后重新安装

    如果安装的库需要其他库的支持, 请根据错误信息, 按照上述方法进行安装


测试相关:

   ltsapi.py 文件: 连接 LTS, 相关 appServer 接口
   testcase/entrorder.py: 下单测试用例
   其中包括:
   1. 下委托单/限价单/市价单
   2. 改单/撤单
   mulorders.py: 对 LTS 进行压力测试
       压力测试时,需要设置好:
       1. 并发的交易账号（包括普通交易账号及 T+0 交易账号）
       2. 交易次数/买入价/卖出价/买入数量/卖出数量/下单 symbol
       3. 下单次数
具体设置如下:
====================
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
========================

可自行补充 LTS 接口进行测试

测试过程中如出现连接失败的情况,重新 run 即可