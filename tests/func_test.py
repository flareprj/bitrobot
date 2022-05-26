from pybit.inverse_perpetual import HTTP
from unittest import TestCase
from modules.strategy import *


class UpdateOrders(TestCase):
    def setUp(self) -> None:
        warnings.simplefilter(action='ignore', category=DeprecationWarning)
        self.api_key = 'kENyGGsOnjJuLvIYqQ'
        self.api_secret = 'jxaVvRLTUqE5ds8CejCTwkYoEUJ9niuovJ1l'
        self.bot = Strategy(test=False, symbol="BTCUSD", api_key=self.api_key,
                            api_secret=self.api_secret, app=None)
        self.data = Endpoints(client=self.bot.client, symbol=self.bot.symbol)
        self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                            api_secret=self.api_secret,
                            recv_window=10000)
        self.side = "Buy"
        self.status = None
        self.timer = 5
        self.interval = "1"
        self.limit = 60
        self.balance = self.bot.data.available_balance()
        self.leverage = 20
        self.percents = 0.1
        self.order_weights = [0.1, 0, 0, 0, 0]

    def test_update_2_orders(self):
        self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_100, self._zone_150, self.zone_150, self.zone_100, \
        self.zone_75, self.zone_50, self.zone_25, df, self.POC, self.price, found_zone_150, found_zone_100, found_zone_75, found_zone_50, \
        found_zone_25, found_zone_150_, found_zone_100_, found_zone_75_, found_zone_50_, found_zone_25_ = self.bot.draw_zones(
            self.interval, self.limit)

        self.arr_l, self.arr_s, qty_l, qty_s = self.bot.count_orders(self.balance, self.leverage, self.interval,
                                                                     self.limit,
                                                                     self.percents, self.order_weights)

        deposit = int(count_deposit(self.price, self.balance, self.leverage, self.percents))
        self.arr_l, self.arr_s = fills(deposit, qty_l, qty_s, self.order_weights)

        self.arr_l.extend(self.arr_s)
        self.arr_l = [x for x in self.arr_l if x != 0]

        try:
            self.bot.create_2_orders(min(self.arr_l), self._zone_150, self._zone_100, self._zone_75,
                                     self._zone_50,
                                     self._zone_25, self.zone_150, self.zone_100,
                                     self.zone_75, self.zone_50, self.zone_25, self.price, self.POC)

        except Exception as e:
            print(repr(e), e)

        i = 10
        while i > 0:
            self.status = self.bot.show_order_status()
            elapsed_time = self.timer
            while elapsed_time > 0 and self.status == "New":
                try:
                    self.status = self.bot.show_order_status()
                    print(f"elapsed_time: {elapsed_time}sec, status:{self.status}")
                    elapsed_time -= 1
                    sleep(1)
                except Exception as e:
                    print('\n', e)
            else:
                print('\ntimer finished!')
                self.bot.cancel_orders()
                print('update levels..')

                self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_100, self._zone_150, self.zone_150, self.zone_100, \
                self.zone_75, self.zone_50, self.zone_25, df, self.POC, self.price, found_zone_150, found_zone_100, found_zone_75, found_zone_50, \
                found_zone_25, found_zone_150_, found_zone_100_, found_zone_75_, found_zone_50_, found_zone_25_ = self.bot.draw_zones(
                    self.interval, self.limit)

                self.arr_l, self.arr_s, qty_l, qty_s = self.bot.count_orders(self.balance, self.leverage, self.interval,
                                                                             self.limit,
                                                                             self.percents, self.order_weights)

                deposit = int(count_deposit(self.price, self.balance, self.leverage, self.percents))
                self.arr_l, self.arr_s = fills(deposit, qty_l, qty_s, self.order_weights)

                self.arr_l.extend(self.arr_s)
                self.arr_l = [x for x in self.arr_l if x != 0]
                print('redraw completed..')
                sleep(1)
                try:
                    self.bot.create_2_orders(min(self.arr_l), self._zone_150, self._zone_100, self._zone_75,
                                             self._zone_50,
                                             self._zone_25, self.zone_150, self.zone_100,
                                             self.zone_75, self.zone_50, self.zone_25, self.price, self.POC)
                    sleep(3)
                except Exception as e:
                    print(repr(e), e)
                else:
                    i -= 1
                    self.status = self.bot.show_order_status()
                    print(f"i:{i}")


class ReplaceStopOrder(TestCase):
    def setUp(self) -> None:
        warnings.simplefilter(action='ignore', category=DeprecationWarning)
        self.api_key = 'kENyGGsOnjJuLvIYqQ'
        self.api_secret = 'jxaVvRLTUqE5ds8CejCTwkYoEUJ9niuovJ1l'
        self.bot = Strategy(test=False, symbol="BTCUSD", api_key='kENyGGsOnjJuLvIYqQ',
                            api_secret='jxaVvRLTUqE5ds8CejCTwkYoEUJ9niuovJ1l', app=None)
        self.data = Endpoints(client=self.bot.client, symbol=self.bot.symbol)
        self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                            api_secret=self.api_secret,
                            recv_window=10000)
        self.side = "Buy"
        self.status = None

    def test_replace_stop_limit(self):
        price = self.data.show_last_price() - 15
        tp = int(price + 500)
        sl = int(price - 150)
        self.session.place_active_order(
            symbol="BTCUSD",
            side="Buy",
            order_type="Limit",
            qty=1,
            price=price,
            time_in_force="GoodTillCancel",
            take_profit=tp,
        )
        res = self.session.place_conditional_order(
            symbol="BTCUSD",
            order_type="Limit",
            side="Sell",
            qty=1,
            price=sl,
            base_price=price,
            stop_px=sl,
            time_in_force="GoodTillCancel",
            close_on_trigger=True
        )
        pprint.pprint(res)
        sleep(5)
        self.status = self.bot.show_order_status()
        while self.status == "New":
            self.status = self.bot.show_order_status()
            print(f"\r{self.status}", end='')
            sleep(1)
        else:
            self.status = self.bot.show_order_status()
            if self.status == "Untriggered":
                sleep(3)
                try:
                    order_id = self.session.get_conditional_order(
                            symbol="BTCUSD"
                     )['result']['data'][0]['stop_order_id']
                    print(order_id)
                    sleep(3)

                    res = self.session.replace_conditional_order(
                            symbol="BTCUSD",
                            stop_order_id=str(order_id),
                            p_r_price=sl+50
                    )
                    pprint.pprint(res)
                    sleep(3)
                    self.status = self.bot.show_order_status()
                except Exception as e:
                    print(e)


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
            price = self.data.show_last_price() - 15
            tp = price + 250
            sl = price - 100
            self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=10, price=price, tp=tp, sl=sl)
        else:
            price = self.data.show_last_price() + 15
            tp = price - 250
            sl = price + 100
            self.data.create_limit_order(side="Sell", symbol="BTCUSD", quantity=10, price=price, tp=tp, sl=sl)

        while True:
            sleep(4)
            try:
                take_profit = float(
                    self.bot.client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0]['result'][
                        'take_profit'])
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
                    trigger_trailing = int(entry_price + ((take_profit - entry_price) / 2))
                else:
                    trigger_trailing = int(entry_price - ((entry_price - take_profit) / 2))

                print(f"trigger_trailing: {trigger_trailing}$")

                while True:
                    active_pos = self.session.my_position(symbol="BTCUSD")['result']['size']
                    if active_pos != 0 and active_pos is not None:
                        try:
                            sleep(2)
                            res = self.session.set_trading_stop(symbol="BTCUSD", take_profit=0, trailing_stop=50,
                                                                new_trailing_active=trigger_trailing)
                            pprint.pprint(res)
                        except Exception as e:
                            print(e)
                        else:
                            if float(self.session.my_position(symbol="BTCUSD")['result']['trailing_stop']) != '0':
                                print(f"placing a trailing-stop: {trigger_trailing}$ - ok! time:{datetime.now()}")
                                return


class WhileLoop(TestCase):
    def setUp(self) -> None:
        self.status_1 = "New"
        self.status_2 = "Untriggered"
        self.status_3 = "Filled"
        self.status_4 = "Cancelled"
        self.status = self.status_4
        self.is_alive = True
        self.timer = 10

    def test_New(self):
        while self.is_alive:
            print(self.status)
            sleep(2)
            if self.status == "New":
                while self.status == "New":
                    elapsed_time = self.timer
                    if self.status == "Untriggered":
                        print('\nstatus is change!')
                        break
                    while elapsed_time > 0:
                        if elapsed_time == 6:
                            self.status = "Untriggered"
                        print(f"elapsed_time: {elapsed_time}sec")
                        elapsed_time -= 1
                        sleep(0.5)
                        if self.status == "Untriggered":
                            print('\nstatus is change!')
                            break
                    else:
                        print('\ntimer finished!')
                        print('update levels..')
                        print('create orders..')

            elif self.status == "Untriggered":
                print('START UNTR BLOCK')
                while self.status == "Untriggered":
                    print('order is process...wait')
                    sleep(2)
                    self.status = "Filled"
                else:
                    print('Stop-Take Order was executed!')
                    print(self.status)
                    print('update levels..')
                    sleep(1)
                    print('create orders..')
                    sleep(1)
                    print('redraw completed..')
                    sleep(1)
                    self.status = "New"
            else:
                sleep(3)
                print('cancel orders if exists')
                sleep(1)
                print('create orders..')
                self.status = "New"
                sleep(1)
