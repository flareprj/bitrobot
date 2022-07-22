import operator
import pprint
import time
import random

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from itertools import accumulate
from time import sleep
from pybit import inverse_perpetual
from PyQt6.QtCore import QThreadPool, pyqtSlot
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

ws_inverse = inverse_perpetual.WebSocket(
    test=False,
    api_key="0ufzW85gpidJWYdN7Q",
    api_secret="eL4uOtCGoUisGxMFwN44lxUDQvwZFkgvniRa",
    domain="bybit",
    ping_interval=30,
    ping_timeout=10
)


# fig = plt.figure(figsize=(8, 5))
# ax = fig.add_subplot(121)
# ax1 = fig.add_subplot(122)
#
# fig.tight_layout()
# fig.show()
#

#
# def update_graph():
#     ax.plot(xdata, ydata, color='g')
#     plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize='x-small')
#     fig.canvas.draw()
#     plt.pause(0.1)


# def show_hist(y, y1):
#     plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='center')
#     plt.setp(ax1.get_xticklabels(), rotation=30, horizontalalignment='center')
#
#     ax.hist(y, bins=35, color='g')
#     ax1.hist(y1, bins=35, color='r')
#
#     ax.axvline(max(y, default=0), color='#fc4f30')
#     ax1.axvline(max(y1, default=0), color='#fc4f30')
#
#     plt.pause(0.05)
#
#     ax.cla()
#     ax1.cla()


def handle_info(message):
    last_price = int(float(message['data']['last_price']))
    event_time = time.localtime(message['timestamp_e6']//10 ** 6)
    event_time = f"{event_time.tm_hour}:{event_time.tm_min}:{event_time.tm_sec}"

    xdata.append(event_time)
    ydata.append(last_price)

    print(last_price, event_time)


def handle_orderbook(message):
    global str_bids, str_asks, ask_price, bid_price, spread

    if len(bids) == 3000:
        del bids[0:1500]
        del asks[0:1500]

    for elem in message['data']:
        for key in elem.keys():
            if elem[key] == "Buy":
                bids.append(elem['size'])
            elif elem[key] == "Sell":
                asks.append(elem['size'])

        for val in elem.values():
            if not bids and not asks:
                pass
            elif bids and asks:
                if val == max(bids) and val > 150000:
                    str_bids = f"{elem['side']} '->' {elem['price']} '->' {val}"
                    bid_price = int(float(elem['price']))
                if val == max(asks) and val > 150000:
                    str_asks = f"{elem['side']} '->' {elem['price']} '->' {val}"
                    ask_price = int(float(elem['price']))
                if bid_price != 0 and ask_price != 0:
                    spread = ask_price-bid_price
                print(f"\r{str_bids}, {str_asks}, spread:{spread}", end='')


ws_inverse.orderbook_25_stream(handle_orderbook, "BTCUSD")
#ws_inverse.instrument_info_stream(handle_info, "BTCUSD")

while True:
    #show_hist(list(accumulate(bids, operator.add)), list(accumulate(asks, operator.add)), bid=bids, ask=asks)
    #show_hist(bids, asks)

    sleep(1)
#    update_graph()

# To subscribe to private data, the process is the same:
# def handle_position(message):
    # I will be called every time there is new position data!
#    print(message)

# ws_inverse.position_stream(handle_position)
