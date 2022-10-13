import datetime
import pprint
from unittest import TestCase
from time import sleep
from datetime import datetime
from pybit.inverse_perpetual import HTTP


class GetTime(TestCase):
    def setUp(self) -> None:
        self.radio = True
        self.symbol = 'BTCUSD'
        self.api_key = ''
        self.api_secret = ''
        if self.radio:
            self.session = HTTP("https://api-testnet.bybit.com", api_key=self.api_key,
                                api_secret=self.api_secret)
        else:
            self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                                api_secret=self.api_secret)

    def create_market(self, side, qty):
        return self.session.place_active_order(
            symbol="BTCUSD",
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel"
        )

    def timer(self, timeframe, limit, position_price, side, qty):
        try:
            time_now_int = int(float(self.session.server_time()['time_now']))
            time_now_int_minus = time_now_int - timeframe * 60 * limit

            result = self.session.query_kline(symbol=self.symbol, interval=str(timeframe),
                                              **{'from': time_now_int_minus},
                                              limit=limit)
            candle_open_time = result['result'][0]['open_time']

            time_now_int = int(float(self.session.server_time()['time_now']))
            open_time_fix = datetime.utcfromtimestamp(int(candle_open_time)).strftime('%H:%M:%S')
        except IndexError as e:
            print(e)
        else:
            while time_now_int < candle_open_time + 60 * timeframe:
                try:
                    time_now_int += 1
                    time_now = datetime.utcfromtimestamp(time_now_int).strftime('%H:%M:%S')
                    sleep(1)
                    print(f'\rcandle_open_time: {open_time_fix}, time_now: {time_now}', end='', flush=True)
                except Exception as e:
                    print(f'timer timeout:{time_now_int}, {e}')
            else:
                print('\nCANDLE FINISH!')
                last_price = round(float(self.session.latest_information_for_symbol(
                    symbol="BTCUSD"
                )['result'][0]['last_price']), 2)
                print(f'last_price: {last_price}$, entry: {position_price}$')

                if last_price-25 <= position_price:
                    print('STOP BLOCK!')
                    if side == 'Buy':
                        lose = self.create_market(side='Sell', qty=qty)
                        print(f'LOSE!!! with {lose}')
                    elif side == 'Sell':
                        lose = self.create_market(side='Buy', qty=qty)
                        print(f'LOSE!!! with {lose}')
                    return 0
                elif side == 'Buy' and last_price >= (position_price + position_price*0.01)/50:
                    self.create_market(side='Sell', qty=qty)
                    print('PROFIT!!!')
                    return 1
                elif side == 'Sell' and last_price <= (position_price - position_price*0.01)/50:
                    self.create_market(side='Buy', qty=qty)
                    print('PROFIT!!!')
                    return 1
                else:
                    print('Nothing happens..')
                    return 0

    def test_filter(self):
        position = self.session.my_position(symbol="BTCUSD")['result']
        qty = position['size']
        print(f'qty: {qty}')

        while True:
            if qty == 0:
                side = 'Buy'
                qty = 1
                trade = self.create_market(side=side, qty=qty)
                position_price = trade['result']['price']
                code = self.timer(1, 1, position_price, side, qty)

                if code == 1:
                    profit = self.session.closed_profit_and_loss(
                        symbol="BTCUSD"
                    )['result']['data'][0]['closed_pnl']
                    profit = '{:0.8f}'.format(profit)
                    print(f'Order was executed with {profit} BTC')
                elif code == 0:
                    print('Continue trade..')
                    sleep(3)
                    position = self.session.my_position(symbol="BTCUSD")['result']
                    qty = position['size']
                    while qty != 0:
                        print('waiting..sleep..')
                        sleep(3)
                        position = self.session.my_position(symbol="BTCUSD")['result']
                        qty = position['size']








