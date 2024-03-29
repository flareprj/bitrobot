import operator
import pprint
import time
import random
from datetime import datetime
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from itertools import accumulate
from time import sleep
from pybit import inverse_perpetual
import pandas as pd
import logging
from matplotlib import interactive

interactive(True)
logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

bids = []
asks = []
str_bids = ''
str_asks = ''
ask_price = 0
bid_price = 0
spread = 0
xdata = []
ydata = []
last_price = 0

ws_inverse = inverse_perpetual.WebSocket(
    test=False,
)
fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(111)

#ax.grid(True)
# fig.tight_layout()


def handle_info(message):
    last_price = int(float(message['data']['last_price']))
    print('before plot:', last_price)
    plt.axvline(x=last_price, color='r')
    # event_time = time.localtime(message['timestamp_e6'] // 10 ** 6)
    # event_time = f"{event_time.tm_hour}:{event_time.tm_min}:{event_time.tm_sec}"

    # xdata.append(event_time)
    # ydata.append(last_price)


def handle_orderbook(message):
    global str_bids, str_asks, ask_price, bid_price, spread, a, b, last_price

    df = pd.DataFrame(message['data'])
    df[['price', 'size']] = df[['price', 'size']].apply(pd.to_numeric, errors='coerce')

    a = df[df.side == 'Buy']
    b = df[df.side == 'Sell']

    a.plot('price', 'size', ax=ax)
    b.plot('price', 'size', ax=ax)

    #plt.axvline(x=last_price, color='r')

    sleep(5)

    # for elem in message['data']:
    #     for key in elem.keys():
    #         if elem[key] == "Buy":
    #             bids.append(elem['size'])
    #         elif elem[key] == "Sell":
    #             asks.append(elem['size'])
    #
    #     for val in elem.values():
    #         if bids and asks:
    #             if val == max(bids) and val > 15000:
    #                 str_bids = f"{elem['side']} '->' {elem['price']} '->' {val}"
    #                 bid_price = int(float(elem['price']))
    #             if val == max(asks) and val > 15000:
    #                 str_asks = f"{elem['side']} '->' {elem['price']} '->' {val}"
    #                 ask_price = int(float(elem['price']))
    #             if bid_price != 0 and ask_price != 0:
    #                 spread = ask_price-bid_price
    # print(f"\r{str_bids}, {str_asks}, spread:{spread}", end='')
    # print(f"{str_bids}, {str_asks}, spread:{spread}")


# if __name__ == '__main__':
#     session_unauth = inverse_perpetual.HTTP(
#         endpoint="https://api-testnet.bybit.com"
#     )
#     res = session_unauth.orderbook(symbol="BTCUSD")['result']
#
#     df = pd.DataFrame(res)
#     pprint.pprint(df)
#     df[['price', 'size']] = df[['price', 'size']].apply(pd.to_numeric, errors='coerce')
#
#     a = df[df.side == 'Buy']
#     b = df[df.side == 'Sell']
#
#     fig, (ax, ax1) = plt.subplots(1, 2)
#
#     a.plot('price', 'size', ax=ax)
#     b.plot('price', 'size', ax=ax1)
#
#     ax.grid(True)
#     ax1.grid(True)
#
#     fig.tight_layout()
#     fig.show()
#
#     plt.show()


ws_inverse.orderbook_200_stream(handle_orderbook, "BTCUSD")
ws_inverse.instrument_info_stream(handle_info, "BTCUSD")

# i = 10
# while i > 0:
#     sleep(1)
#     fig.show()
#     plt.show()
#
#     path = 'img/' + f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg'
#     plt.savefig(path)
#
#     plt.pause(2)
#     sleep(1)
#     ax.cla()
#     i -= 1


while True:
    sleep(1)
    fig.show()
    plt.show()

    path = 'img/' + f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg'
    plt.savefig(path)

    plt.pause(2)
    sleep(1)
    ax.cla()
