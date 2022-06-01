from unittest import TestCase
from modules.strategy import *


class LimitOrder(TestCase):

    def setUp(self) -> None:
        warnings.simplefilter(action='ignore', category=DeprecationWarning)
        self.bot = Strategy(test=True, symbol="BTCUSD", api_key='qwZENih1NkKLge7kZX',
                       api_secret='ptnypkd2W3DfiB82RX1wQUi9ThQSgvPqiCBh', app=None)
        self.data = Endpoints(client=self.bot.client, symbol=self.bot.symbol)

    def create_limit(self):
        price = self.data.show_last_price()-1500
        tp = price+250
        sl = price-100

        self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=100, price=price, tp=tp, sl=sl)
        self.data.create_close_order(side="Sell", symbol="BTCUSD", quantity=100, price=price, tp=tp)

        # self.assertFalse(self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=-100, price=price, tp=tp, sl=sl))
        # self.assertFalse(self.data.create_limit_order(side="Buy", symbol="BT1CUSD", quantity=100, price=price, tp=tp, sl=sl))
        # self.assertFalse(self.data.create_limit_order(side="B1uy", symbol="BTCUSD", quantity=100, price=price, tp=tp, sl=sl))

