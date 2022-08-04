import unittest
from unittest import TestCase
from modules.strategy import *
from pybit.inverse_perpetual import HTTP


class LimitOrder(TestCase):
    def setUp(self) -> None:
        warnings.simplefilter(action='ignore', category=DeprecationWarning)
        self.api_key = '0ufzW85gpidJWYdN7Q'
        self.api_secret = 'eL4uOtCGoUisGxMFwN44lxUDQvwZFkgvniRa'

        self.api_key_test = 'qwZENih1NkKLge7kZX'
        self.api_secret_test = 'ptnypkd2W3DfiB82RX1wQUi9ThQSgvPqiCBh'

        self.bot = Strategy(test=False, symbol="BTCUSD", api_key=self.api_key,
                            api_secret=self.api_secret, app=None)
        self.data = Endpoints(client=self.bot.client, symbol=self.bot.symbol)
        self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                            api_secret=self.api_secret)

        self.side = "Both"
        self.delta = 25

    def test_create_limit(self):
        while True:
            price = self.data.show_last_price() - 50
            tp = price + 200
            buy_1 = self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=1, price=price + self.delta,
                                                 tp=tp, sl=0)
            buy_2 = self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=1, price=price, tp=0, sl=0)
            buy_3 = self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=1, price=price - self.delta,
                                                 tp=0,
                                                 sl=price - self.delta * 2)

            price = self.data.show_last_price() + 50
            tp = price - 200
            sell_1 = self.data.create_limit_order(side="Sell", symbol="BTCUSD", quantity=1, price=price - self.delta,
                                                  tp=tp, sl=0)
            sell_2 = self.data.create_limit_order(side="Sell", symbol="BTCUSD", quantity=1, price=price, tp=0, sl=0)
            sell_3 = self.data.create_limit_order(side="Sell", symbol="BTCUSD", quantity=1, price=price + self.delta,
                                                  tp=0,
                                                  sl=price + self.delta * 2)

            buy_list = [buy_1[0]['result']['order_id'], buy_2[0]['result']['order_id'], buy_3[0]['result']['order_id']]
            sell_list = [sell_1[0]['result']['order_id'], sell_2[0]['result']['order_id'], sell_3[0]['result']['order_id']]

            self.is_orders = True
            self.sl_change = False

            def cancel_orders(side_):
                if side_ == 'Buy' and self.is_orders:
                    for order_id in sell_list:
                        if not isinstance(order_id, bool):
                            self.session.cancel_active_order(
                                symbol="BTCUSD",
                                order_id=order_id
                            )
                    self.is_orders = False
                elif side_ == 'Sell' and self.is_orders:
                    for order_id in buy_list:
                        if not isinstance(order_id, bool):
                            self.session.cancel_active_order(
                                symbol="BTCUSD",
                                order_id=order_id
                            )
                    self.is_orders = False

            def execution_wait():
                print(f"waiting..")
                sleep(1)

            position_size = self.session.my_position(symbol="BTCUSD")['result']['size']

            while position_size == 0:
                execution_wait()
                position_size = self.session.my_position(symbol="BTCUSD")['result']['size']
            else:
                try:
                    req_pos = self.session.my_position(symbol="BTCUSD")['result']
                except Exception as e:
                    print(e)
                else:
                    take_profit = float(req_pos['take_profit'])
                    entry_price = float(req_pos['entry_price'])
                    side = req_pos['side']

                    print(f"take_profit: {take_profit}")
                    print(f"entry_price: {entry_price}")
                    print(f"side: {side}")

                    cancel_orders(side)

                    if side == "Buy":
                        if take_profit == 0:
                            take_profit = entry_price + 200
                        trigger_trailing = int(entry_price + ((take_profit - entry_price) / 2))
                        print(f"trigger_trailing: {trigger_trailing}$")
                    if side == "Sell":
                        if take_profit == 0:
                            take_profit = entry_price - 200
                        trigger_trailing = int(entry_price - ((entry_price - take_profit) / 2))
                        print(f"trigger_trailing: {trigger_trailing}$")

                    while True:
                        req_pos = self.session.my_position(symbol="BTCUSD")['result']
                        position_size = req_pos['side']

                        if position_size != 0:
                            try:
                                self.session.set_trading_stop(symbol="BTCUSD", take_profit=0,
                                                              trailing_stop=25,
                                                              new_trailing_active=trigger_trailing)
                            except Exception as e:
                                print('error while placing trailing-stop!', e)
                                continue
                            else:
                                if float(self.session.my_position(symbol="BTCUSD")['result'][
                                             'trailing_stop']) != '0':
                                    print(
                                        f"placing a trailing-stop: {trigger_trailing}$ - ok! time:{datetime.now()}")
                                    break

                    while position_size != 0:
                        try:
                            position_size = self.session.my_position(symbol="BTCUSD")['result']['size']
                            price = self.bot.get_live_price()
                            live_pnl = self.bot.get_live_pnl()
                            print(f"PNL: {live_pnl}, size: {position_size}")

                            delta_breakeven = 25

                            if side == "Buy" and float(price) > float(trigger_trailing - 50) + delta_breakeven and not self.sl_change:
                                print('Entering buy block!')
                                try:
                                    res = self.session.set_trading_stop(symbol="BTCUSD", stop_loss=int(
                                        entry_price + ((trigger_trailing - entry_price) / 2)))
                                    if res['ret_code'] == 0:
                                        print(f'\nSL has been replaced! New price:{res["result"]["stop_loss"]}$')
                                        logger.info(f'SL has been replaced! New price:{res["result"]["stop_loss"]}$')
                                        self.sl_change = True
                                except Exception as e:
                                    print(e)

                            if side == "Sell" and float(price) < float(trigger_trailing + 50) - delta_breakeven and not self.sl_change:
                                print('Entering sell block!')
                                try:
                                    res = self.session.set_trading_stop(symbol="BTCUSD", stop_loss=int(
                                        entry_price - ((entry_price - trigger_trailing) / 2)))
                                    if res['ret_code'] == 0:
                                        print(f'\nSL has been replaced! New price: {res["result"]["stop_loss"]}$')
                                        logger.info(f'SL has been replaced! New price: {res["result"]["stop_loss"]}$')
                                        self.sl_change = True
                                except Exception as e:
                                    print(e)
                            sleep(3)
                        except Exception as e:
                            print(e)
                    else:
                        print(f"Order was executed! Position size: {position_size}")
                        self.bot.cancel_orders()
