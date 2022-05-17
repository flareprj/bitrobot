from pybit.inverse_perpetual import HTTP
from unittest import TestCase
from modules.strategy import *


class LimitOrder(TestCase):

    def setUp(self) -> None:
        warnings.simplefilter(action='ignore', category=DeprecationWarning)
        self.api_key = 'qwZENih1NkKLge7kZX'
        self.api_secret = 'ptnypkd2W3DfiB82RX1wQUi9ThQSgvPqiCBh'
        self.bot = Strategy(test=True, symbol="BTCUSD", api_key='qwZENih1NkKLge7kZX',
                       api_secret='ptnypkd2W3DfiB82RX1wQUi9ThQSgvPqiCBh', app=None)
        self.data = Endpoints(client=self.bot.client, symbol=self.bot.symbol)
        self.session = HTTP("https://api-testnet.bybit.com", api_key=self.api_key,
                       api_secret=self.api_secret,
                       recv_window=10000)

        self.side = "Buy"

    def test_create_limit(self):
        if self.side == "Buy":
            price = self.data.show_last_price()-15
            tp = price+250
            sl = price-100
            self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=10, price=price, tp=tp, sl=sl)
        else:
            price = self.data.show_last_price()+15
            tp = price-250
            sl = price+100
            self.data.create_limit_order(side="Sell", symbol="BTCUSD", quantity=10, price=price, tp=tp, sl=sl)

        while True:
            sleep(4)
            try:
                take_profit = float(self.bot.client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0]['result']['take_profit'])
                last_price = float(self.bot.get_live_price())
                entry_price = price

                print(f"take_profit: {take_profit}")
                print(f"last_price: {last_price}")
                print(f"entry_price: {entry_price}")

            except Exception as e:
                print(e)
            else:
                while take_profit == 0:
                    take_profit = float(
                        self.bot.client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0]['result'][
                            'take_profit'])
                    sleep(1)

                if take_profit > entry_price != 0 and take_profit != 0:
                    trigger_trailing = int(entry_price + ((take_profit - entry_price)/2))
                else:
                    trigger_trailing = int(entry_price - ((entry_price - take_profit) / 2))

                print(f"trigger_trailing: {trigger_trailing}$")

                while True:
                    active_pos = self.session.my_position(symbol="BTCUSD")['result']['size']
                    if active_pos != 0 and active_pos is not None:
                        try:
                            sleep(2)
                            res = self.session.set_trading_stop(symbol="BTCUSD", take_profit=0, trailing_stop=50, new_trailing_active=trigger_trailing)
                            pprint.pprint(res)
                        except Exception as e:
                            print(e)
                        else:
                            if float(self.session.my_position(symbol="BTCUSD")['result']['trailing_stop']) != '0':
                                print(f"placing a trailing-stop: {trigger_trailing}$ - ok! time:{datetime.now()}")
                                return
