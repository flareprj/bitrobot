import http.client
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
        self.api_key = ''
        self.api_secret = ''
        self.bot = Strategy(test=False, symbol="BTCUSD", api_key='',
                            api_secret='', app=None)
        self.data = Endpoints(client=self.bot.client, symbol=self.bot.symbol)
        self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                            api_secret=self.api_secret,
                            recv_window=10000)
        self.side = None
        self.status = None

    def test_replace_stop_limit(self):
        price_l = self.data.show_last_price() - 200
        price_s = self.data.show_last_price() + 200

        tp_l = int(price_l + 200)
        sl_l = int(price_l - 150)

        tp_s = int(price_s - 200)
        sl_s = int(price_s + 150)

        self.session.place_active_order(
            symbol="BTCUSD",
            side="Buy",
            order_type="Limit",
            qty=1,
            price=price_l,
            time_in_force="GoodTillCancel",
            take_profit=tp_l,
        )

        self.session.place_active_order(
            symbol="BTCUSD",
            side="Sell",
            order_type="Limit",
            qty=1,
            price=price_s,
            time_in_force="GoodTillCancel",
            take_profit=tp_s,
        )

        self.session.place_conditional_order(
            symbol="BTCUSD",
            order_type="Limit",
            side="Sell",
            qty=1,
            price=sl_l,
            base_price=price_l,
            stop_px=sl_l,
            time_in_force="GoodTillCancel",
            close_on_trigger=True
        )

        self.session.place_conditional_order(
            symbol="BTCUSD",
            order_type="Limit",
            side="Buy",
            qty=1,
            price=sl_s,
            base_price=price_s,
            stop_px=sl_s,
            time_in_force="GoodTillCancel",
            close_on_trigger=True
        )

        while self.status == "New":
            print(f"{self.status}")
            sleep(1)
        else:
            self.side = self.session.get_active_order(
                symbol="BTCUSD",
                order_status="Filled,New"
            )['result']['order_side']
            print(self.side)

            self.session.get_conditional_order(
                symbol="BTCUSD",
                stop_order_status="Untriggered"
            )


class LimitOrder(TestCase):
    def setUp(self) -> None:
        warnings.simplefilter(action='ignore', category=DeprecationWarning)
        self.api_key = 'qwZENih1NkKLge7kZX'
        self.api_secret = 'ptnypkd2W3DfiB82RX1wQUi9ThQSgvPqiCBh'
        self.bot = Strategy(test=False, symbol="BTCUSD", api_key='qwgV06Je2in5PICYGW',
                            api_secret='vcflzZbd3PfnXxYD30x8Yj6XJ2l9ndq4bcrP', app=None)
        self.data = Endpoints(client=self.bot.client, symbol=self.bot.symbol)
        self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                            api_secret=self.api_secret)

        self.side = "Buy"

    def test_create_limit(self):
        if self.side == "Buy":
            price = self.data.show_last_price() - 15
            tp = price + 250
            sl = price - 100
            self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=1, price=price, tp=tp, sl=sl)
        else:
            price = self.data.show_last_price() + 15
            tp = price - 250
            sl = price + 100
            self.data.create_limit_order(side="Sell", symbol="BTCUSD", quantity=1, price=price, tp=tp, sl=sl)

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
        warnings.simplefilter(action='ignore', category=DeprecationWarning)
        self.api_key = 'qwgV06Je2in5PICYGW'
        self.api_secret = 'vcflzZbd3PfnXxYD30x8Yj6XJ2l9ndq4bcrP'
        self.bot = Strategy(test=False, symbol="BTCUSD", api_key='qwgV06Je2in5PICYGW',
                            api_secret='vcflzZbd3PfnXxYD30x8Yj6XJ2l9ndq4bcrP', app=None)
        self.data = Endpoints(client=self.bot.client, symbol=self.bot.symbol)
        self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                            api_secret=self.api_secret)
        self.timer = 5
        self.price = self.data.show_last_price()

    def test_New(self):
        self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=1, price=self.price-15, tp=self.price+100, sl=self.price-50)
        self.data.create_limit_order(side="Sell", symbol="BTCUSD", quantity=1, price=self.price+15, tp=self.price-100, sl=self.price+50)
        sleep_()
        while True:
            self.status = self.bot.show_order_status()
            print(f'current_status: {self.status}')
            if self.status == "New":
                elapsed_time = self.timer
                while elapsed_time > 0 and self.status == "New":
                    self.status = self.bot.show_order_status()
                    if self.status == "Untriggered":
                        break
                    print(f"\relapsed_time: {elapsed_time}sec", end='')
                    elapsed_time -= 1
                    sleep(1)
            elif self.status == "Untriggered":
                print("We have Untriggered order! Cancel another orders!")
                self.bot.cancel_orders()
                #sleep_()
                try:
                    self.status = self.bot.show_order_status()
                    order_id = \
                        self.bot.client.Order.Order_getOrders(symbol="BTCUSD",
                                                              order_status="Untriggered").result()[
                            0]['result']['data'][0]['order_id']
                except Exception as e:
                    print(e)
                    logger.exception(e, exc_info=True)
                    if self.status != "Untriggered":
                        self.status = self.bot.show_order_status()
                        # На случай, если произошло очень резкое исполнение
                        if self.status == "Filled":
                            self.bot.cancel_orders()
                        print(f'current_status: {self.status}')
                        sleep(1)
                else:
                    print(f"untriggered_order_id:{order_id}")
                    while self.status == "Untriggered":
                        try:
                            sleep(1)
                            take_profit = float(
                                self.bot.client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0][
                                    'result']['take_profit'])
                            last_price = float(self.bot.get_live_price())
                            entry_price = float(self.session.my_position(symbol="BTCUSD")['result']['entry_price'])
                            side = self.session.my_position(symbol="BTCUSD")['result']['side']

                            print(f"take_profit: {take_profit}")
                            print(f"last_price: {last_price}")
                            print(f"entry_price: {entry_price}")
                            print(f"side: {side}")

                        except http.client.RemoteDisconnected as e:
                            print(repr(e), e)
                            logger.error(f"RemoteDisconnected, {e}")
                            sleep_()
                        except requests.exceptions.ConnectionError as e:
                            print(repr(e), e)
                            logger.exception(repr(e), e, exc_info=True)
                            sleep_()
                        except Exception as e:
                            print(repr(e), e)
                            logger.exception(repr(e), e, exc_info=True)
                            sleep_()
                        else:
                            if take_profit > entry_price:
                                trigger_trailing = int(entry_price + ((take_profit - entry_price) / 2))
                                print(f"\ntrigger_trailing: {trigger_trailing}$")
                                logger.info(f"trigger_trailing: {trigger_trailing}$")
                            elif take_profit < entry_price:
                                trigger_trailing = int(entry_price - abs((take_profit - entry_price) / 2))
                                print(f"\ntrigger_trailing: {trigger_trailing}$")
                                logger.info(f"trigger_trailing: {trigger_trailing}$")
                            else:
                                break

                            while True:
                                active_pos = self.session.my_position(symbol="BTCUSD")['result']['size']
                                if active_pos != 0 and active_pos is not None:
                                    try:
                                        self.session.set_trading_stop(symbol="BTCUSD", take_profit=0,
                                                                      trailing_stop='25',
                                                                      new_trailing_active=trigger_trailing)
                                    except Exception as e:
                                        print(e)
                                        logger.exception(f"{e}", exc_info=True)
                                        sleep_()
                                    else:
                                        if float(self.session.my_position(symbol="BTCUSD")['result'][
                                                     'trailing_stop']) != '0':
                                            print(
                                                f"placing a trailing-stop: {trigger_trailing}$ - ok! time:{datetime.now()}")
                                            logger.info(f"placing a trailing-stop: {trigger_trailing}$ - ok!")
                                            break

                            while self.status == "Untriggered":
                                try:
                                    self.status = self.bot.show_order_status()
                                    live_pnl = str(self.bot.get_live_pnl()) + ' BTC'
                                    print(f"\r{live_pnl}, entry_price:{entry_price}$", end='')
                                    sleep_()
                                    if self.status != "Untriggered":
                                        print(f"IF BLOCK, {self.status}")
                                        logger.info(f"IF BLOCK, {self.status}")
                                        break
                                except http.client.RemoteDisconnected as e:
                                    logger.error(f"RemoteDisconnected, {e}")
                                    sleep_()
                                except Exception as e:
                                    print(e)
                                    logger.exception(repr(e), e, exc_info=True)
                                    sleep_()

                    print(f'\nStop-Take Order was executed! time:{datetime.now()}')
                    self.bot.cancel_orders()
                    self.price = self.data.show_last_price()
                    self.data.create_limit_order(side="Buy", symbol="BTCUSD", quantity=1, price=self.price - 15,
                                                 tp=self.price + 100, sl=self.price - 50)
                    self.data.create_limit_order(side="Sell", symbol="BTCUSD", quantity=1, price=self.price + 15,
                                                 tp=self.price - 100, sl=self.price + 50)
                    self.status = self.bot.show_order_status()
                    while self.status != "New":
                        self.status = self.bot.show_order_status()
                        # На случай, если произошло очень резкое исполнение
                        if self.status == "Filled":
                            self.bot.cancel_orders()
                        print(f'current_status: {self.status}')
                        sleep(1)
