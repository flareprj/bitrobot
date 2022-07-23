from time import sleep
from pybit import inverse_perpetual as inverse

buy_list = {}
sell_list = {}
a = 0
b = 0


def handle_orderbook(message):
    global a
    global b
    buy_list = {}
    sell_list = {}
    buy_price = []
    sell_price = []
    orderbook_data = message["data"]
    print(orderbook_data)

    for x in orderbook_data:
        if x['side'] == 'Buy':
            buy_list[x['price']] = x['size']
            buy_price.append(x['price'])
        if x['side'] == 'Sell':
            sell_list[x['price']] = x['size']
            sell_price.append(x['price'])

    sell_list = dict(sorted(sell_list.items()))
    buy_list = dict(sorted(buy_list.items()))
    sell_price = sorted(sell_price)
    buy_price = sorted(buy_list)

    print(buy_price[-1], sell_price[0])
    print('--------------')

    sleep(1)


ws = inverse.WebSocket(test=True)
ws.orderbook_25_stream(handle_orderbook, 'BTCUSD')

while True:
    sleep(1)
