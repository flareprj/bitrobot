import unittest
from unittest import TestCase
from modules.strategy import *


SETUP_COUNTER = 0


class MyTestCase(TestCase):

    def setUp(self) -> None:
        warnings.simplefilter(action='ignore', category=DeprecationWarning)
        self.api_key = ''
        self.api_secret = ''
        self.bot = Strategy(test=False, symbol="BTCUSD", api_key=self.api_key,
                            api_secret=self.api_secret, app=None)
        self.balance = self.bot.data.available_balance()
        self.leverage = 5
        self.interval = '15'
        self.limit = 200
        self.percents = 0.5
        self.order_weights = [0.1, 0.19, 0.3, 0.45, 1]

    def test_one(self):
        status = self.bot.show_order_status()
        if status == 'New':
            self.bot.cancel_orders()
            sleep(2)
        self.arr_l, self.arr_s, qty_l, qty_s = self.bot.count_orders(self.balance, self.leverage, self.interval,
                                                                     self.limit,
                                                                     self.percents, self.order_weights)

        self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_100, self._zone_150, self.zone_150, self.zone_100, \
        self.zone_75, self.zone_50, self.zone_25, df, self.POC, self.price, found_zone_150, found_zone_100, found_zone_75, found_zone_50, \
        found_zone_25, found_zone_150_, found_zone_100_, found_zone_75_, found_zone_50_, found_zone_25_ = self.bot.draw_zones(
            self.interval, self.limit)

        print(self.arr_l, self.arr_s)

        self.bot.create_2_orders(self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100,
                        self.zone_75, self.zone_50, self.zone_25, self.price, self.POC)


def suite():
    tests = []
    for _ in range(100):
        tests.append('test_one')

    return unittest.TestSuite(map(MyTestCase, tests))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
    print('setUp was run', SETUP_COUNTER, 'times')

