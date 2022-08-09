import bybit
import warnings
import pandas as pd
import numpy as np
from scipy import stats, signal
import csv
import pathlib
from modules.functions import *
from modules.orders_calc import *
from modules.exceptions import *

warnings.simplefilter(action='ignore', category=FutureWarning)


class Strategy:
    def __init__(self, test, symbol, api_key, api_secret, app):
        self.client = bybit.bybit(test=test, api_key=api_key, api_secret=api_secret)
        self.symbol = symbol
        self.data = Endpoints(client=self.client, symbol=self.symbol)
        self.app = app

    def cancel_orders(self):
        try:
            result = self.client.Order.Order_cancelAll(symbol=self.symbol).result()
        except Exception as e:
            print(e)
            logger.exception(f"{e}", exc_info=True)
        else:
            result_code = result[0]['ret_code']
            if result_code == 0:
                print('\nAll orders cancelled successfully!')
                logger.info('All orders cancelled successfully!')
                return 'All orders cancelled successfully!'
            else:
                print(f"Error with code: {result_code}!")
                logger.error(f"Error with code: {result_code}!")
                return f"Error with code: {result_code}!"

    def show_order_status(self):
        try:
            result = self.client.Order.Order_getOrders(symbol=self.symbol).result()[0]['result']['data'][0][
                'order_status']
        except Exception as e:
            print(e)
            logger.exception(f"{e}", exc_info=True)
            sleep_()
        else:
            if result is not None:
                return result

    def get_live_pnl(self):
        try:
            result = self.client.Positions.Positions_myPosition(symbol=self.symbol).result()[0]['result'][
                'unrealised_pnl']
            if result == 0:
                return result
            elif result is not None:
                result = '{:0.8f}'.format(result)
                return result
        except Exception as e:
            print(e)
            logger.exception(f"{e}", exc_info=True)
            sleep_()

    def get_live_price(self):
        return str(self.data.show_last_price())

    def get_kline(self, interval: str, limit: int):
        allowed = ['1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M']
        if interval in allowed:
            try:
                time_now_int = int(float(self.client.Common.Common_getTime().result()[0]["time_now"]))
                return {
                    '1': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='1',
                                                                                 **{'from': time_now_int - int(
                                                                                     '1') * 60 * limit},
                                                                                 limit=limit).result(),
                    '3': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='3',
                                                                                 **{'from': time_now_int - int(
                                                                                     '3') * 60 * limit},
                                                                                 limit=limit).result(),
                    '5': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='5',
                                                                                 **{'from': time_now_int - int(
                                                                                     '5') * 60 * limit},
                                                                                 limit=limit).result(),
                    '15': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='15',
                                                                                  **{'from': time_now_int - int(
                                                                                      '15') * 60 * limit},
                                                                                  limit=limit).result(),
                    '30': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='30',
                                                                                  **{'from': time_now_int - int(
                                                                                      '30') * 60 * limit},
                                                                                  limit=limit).result(),
                    '60': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='60',
                                                                                  **{'from': time_now_int - int(
                                                                                      '60') * 60 * limit},
                                                                                  limit=limit).result(),
                    '120': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='120',
                                                                                   **{'from': time_now_int - int(
                                                                                       '120') * 60 * limit},
                                                                                   limit=limit).result(),
                    '240': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='240',
                                                                                   **{'from': time_now_int - int(
                                                                                       '240') * 60 * limit},
                                                                                   limit=limit).result(),
                    '360': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='360',
                                                                                   **{'from': time_now_int - int(
                                                                                       '360') * 60 * limit},
                                                                                   limit=limit).result(),
                    '720': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='720',
                                                                                   **{'from': time_now_int - int(
                                                                                       '720') * 60 * limit},
                                                                                   limit=limit).result(),
                    'D': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='D',
                                                                                 **{
                                                                                     'from': time_now_int - 24 * 60 * 60 * limit},
                                                                                 limit=limit).result(),
                    'W': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='W',
                                                                                 **{
                                                                                     'from': time_now_int - 24 * 7 * 60 * 60 * limit},
                                                                                 limit=limit).result(),
                    'M': lambda time_now_int, limit: self.client.Kline.Kline_get(symbol=self.symbol, interval='M',
                                                                                 **{
                                                                                     'from': time_now_int - 24 * 30 * 60 * 60 * limit},
                                                                                 limit=limit).result(),
                }[interval](time_now_int, limit)
            except Exception as e:
                print(e)
                logger.exception(f"{e}", exc_info=True)
        else:
            print('Incorrect timeframe or limit!')
            logger.error('Incorrect timeframe or limit!')

    def get_balance(self):
        while self.data.available_balance() is None:
            sleep(1)
        else:
            balance = self.data.available_balance()
            return balance

    def count_orders(self, balance, leverage, interval, limit, percent, order_weights):
        self.data.set_leverage(leverage)
        price = self.data.show_last_price()
        percent = round(float(percent), 2)
        overall_contracts = self.count_contracts(price, balance, leverage=leverage, percent=percent)
        data_kline = Strategy.get_kline(self, interval=interval, limit=limit)

        _zone_150, _zone_100, _zone_75, _zone_50, _zone_25, zone_150, zone_100, \
        zone_75, zone_50, zone_25, df, POC = Strategy.get_margin_poc(
            data_kline)

        qty_l = qty_s = 0

        qty_l += 1 if price > _zone_150 else 0
        qty_l += 1 if price > _zone_100 else 0
        qty_l += 1 if price > _zone_75 else 0
        qty_l += 1 if price > _zone_50 else 0
        qty_l += 1 if price > _zone_25 else 0

        qty_s += 1 if price < zone_150 else 0
        qty_s += 1 if price < zone_100 else 0
        qty_s += 1 if price < zone_75 else 0
        qty_s += 1 if price < zone_50 else 0
        qty_s += 1 if price < zone_25 else 0

        arr_l, arr_s = calc_orders(overall_contracts, qty_l, qty_s, order_weights)
        return arr_l, arr_s, qty_l, qty_s

    def create_orders(self, arr_l, arr_s, _zone_150, _zone_100, _zone_75, _zone_50, _zone_25, zone_150, zone_100,
                      zone_75, zone_50, zone_25, price, POC):

        logger.info(f'Start creating orders with: {arr_l}, {_zone_150}, {_zone_100}, {_zone_75}, {_zone_50}, {_zone_25}, {zone_150}, {zone_100}, {zone_75}, {zone_50}, {zone_25}, {price}, {POC}')

        delta = int((_zone_25 - _zone_50) / 2)

        if price > _zone_25:
            self.data.create_limit_order("Buy", self.symbol, arr_l[0], _zone_25, tp=POC,
                                         sl=_zone_25 - delta)
        if price > _zone_50:
            self.data.create_limit_order("Buy", self.symbol, arr_l[1], _zone_50, tp=_zone_25,
                                         sl=_zone_50 - delta)
        if price > _zone_75:
            self.data.create_limit_order("Buy", self.symbol, arr_l[2], _zone_75, tp=_zone_50,
                                         sl=_zone_75 - delta)
        if price > _zone_100:
            self.data.create_limit_order("Buy", self.symbol, arr_l[3], _zone_100, tp=_zone_75,
                                         sl=_zone_100 - delta)
        if price > _zone_150:
            self.data.create_limit_order("Buy", self.symbol, arr_l[4], _zone_150, tp=_zone_100,
                                         sl=_zone_150 - delta)

        if price < zone_25:
            self.data.create_limit_order("Sell", self.symbol, arr_s[0], zone_25, tp=POC,
                                         sl=zone_25 + delta)
        if price < zone_50:
            self.data.create_limit_order("Sell", self.symbol, arr_s[1], zone_50, tp=zone_25,
                                         sl=zone_50 + delta)
        if price < zone_75:
            self.data.create_limit_order("Sell", self.symbol, arr_s[2], zone_75, tp=zone_50,
                                         sl=zone_75 + delta)
        if price < zone_100:
            self.data.create_limit_order("Sell", self.symbol, arr_s[3], zone_100, tp=zone_75,
                                         sl=zone_100 + delta)
        if price < zone_150:
            self.data.create_limit_order("Sell", self.symbol, arr_s[4], zone_150, tp=zone_100,
                                         sl=zone_150 + delta)

    def create_6_orders(self, arr_l, _zone_150, _zone_100, _zone_75, _zone_50, _zone_25, zone_150, zone_100,
                        zone_75, zone_50, zone_25, price, POC):

        logger.info(f'Start creating orders with: {arr_l}, {_zone_150}, {_zone_100}, {_zone_75}, {_zone_50}, {_zone_25}, {zone_150}, {zone_100}, {zone_75}, {zone_50}, {zone_25}, {price}, {POC}')
        delta = 33
        check_levels = 0
        if check_levels == 0:
            if price > _zone_25:
                buy_1 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_25 + delta, tp=POC, sl=0)
                buy_2 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_25, tp=0, sl=0)
                buy_3 = self.data.create_limit_order("Buy", self.symbol, quantity=2*arr_l, price=_zone_25 - 2*delta, tp=0, sl=(_zone_25 - 2*delta)-round((_zone_25-_zone_50)/2, 2))
                buy_list = [buy_1[0]['result']['order_id'], buy_2[0]['result']['order_id'],
                            buy_3[0]['result']['order_id']]
            elif price > _zone_50:
                buy_1 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_50 + delta, tp=_zone_25+delta, sl=0)
                buy_2 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_50, tp=0, sl=0)
                buy_3 = self.data.create_limit_order("Buy", self.symbol, quantity=2*arr_l, price=_zone_50 - 2*delta, tp=0, sl=(_zone_50 - 2 * delta)-round((_zone_50-_zone_75)/2, 2))

                buy_list = [buy_1[0]['result']['order_id'], buy_2[0]['result']['order_id'],
                            buy_3[0]['result']['order_id']]
            elif price > _zone_75:
                buy_1 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_75 + delta, tp=_zone_50+delta, sl=0)
                buy_2 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_75, tp=0, sl=0)
                buy_3 = self.data.create_limit_order("Buy", self.symbol, quantity=2*arr_l, price=_zone_75 - 2*delta, tp=0, sl=(_zone_75 - 2 * delta)-round((_zone_50-_zone_75)/2, 2))

                buy_list = [buy_1[0]['result']['order_id'], buy_2[0]['result']['order_id'],
                            buy_3[0]['result']['order_id']]
            elif price > _zone_100:
                buy_1 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_100 + delta, tp=_zone_75+delta, sl=0)
                buy_2 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_100, tp=0, sl=0)
                buy_3 = self.data.create_limit_order("Buy", self.symbol, quantity=2*arr_l, price=_zone_100 - 2*delta, tp=0, sl=(_zone_100 - 2 * delta)-round((_zone_100-_zone_150)/2, 2))

                buy_list = [buy_1[0]['result']['order_id'], buy_2[0]['result']['order_id'],
                            buy_3[0]['result']['order_id']]
            elif price > _zone_150:
                buy_1 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_150 + delta, tp=_zone_100+delta, sl=0)
                buy_2 = self.data.create_limit_order("Buy", self.symbol, quantity=arr_l, price=_zone_150, tp=0, sl=0)
                buy_3 = self.data.create_limit_order("Buy", self.symbol, quantity=2*arr_l, price=_zone_150 - 2*delta, tp=0, sl=(_zone_150 - 2 * delta)-round((_zone_100-_zone_150)/2, 2))

                buy_list = [buy_1[0]['result']['order_id'], buy_2[0]['result']['order_id'],
                            buy_3[0]['result']['order_id']]

            else:
                print(f'Longs not found! POC:{POC}, price:{price}')
                logger.info(f'Longs not found! POC:{POC}, price:{price}')
                check_levels = 1
                return None, None, check_levels

        if check_levels == 0:
            if price < zone_25:
                sell_1 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_25-delta, tp=POC, sl=0)
                sell_2 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_25, tp=0, sl=0)
                sell_3 = self.data.create_limit_order("Sell", self.symbol, quantity=2*arr_l, price=zone_25+2*delta, tp=0, sl=(zone_25+2*delta)+round((zone_50-zone_25)/2, 2))
                sell_list = [sell_1[0]['result']['order_id'], sell_2[0]['result']['order_id'],
                             sell_3[0]['result']['order_id']]
                return buy_list, sell_list, check_levels
            elif price < zone_50:
                sell_1 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_50-delta, tp=zone_25-delta, sl=0)
                sell_2 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_50, tp=0, sl=0)
                sell_3 = self.data.create_limit_order("Sell", self.symbol, quantity=2*arr_l, price=zone_50+2*delta, tp=0, sl=(zone_50+2*delta)+round((zone_75-zone_50)/2, 2))
                sell_list = [sell_1[0]['result']['order_id'], sell_2[0]['result']['order_id'],
                             sell_3[0]['result']['order_id']]
                return buy_list, sell_list, check_levels
            elif price < zone_75:
                sell_1 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_75-delta, tp=zone_50-delta, sl=0)
                sell_2 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_75, tp=0, sl=0)
                sell_3 = self.data.create_limit_order("Sell", self.symbol, quantity=2*arr_l, price=zone_75+2*delta, tp=0, sl=(zone_75+2*delta)+round((zone_100-zone_75)/2, 2))
                sell_list = [sell_1[0]['result']['order_id'], sell_2[0]['result']['order_id'],
                             sell_3[0]['result']['order_id']]
                return buy_list, sell_list, check_levels
            elif price < zone_100:
                sell_1 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_100-delta, tp=zone_75-delta, sl=0)
                sell_2 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_100, tp=0, sl=0)
                sell_3 = self.data.create_limit_order("Sell", self.symbol, quantity=2*arr_l, price=zone_100+2*delta, tp=0, sl=(zone_100+2*delta)+round((zone_150-zone_100)/2, 2))
                sell_list = [sell_1[0]['result']['order_id'], sell_2[0]['result']['order_id'],
                             sell_3[0]['result']['order_id']]
                return buy_list, sell_list, check_levels
            elif price < zone_150:
                sell_1 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_150-delta, tp=zone_100-delta, sl=0)
                sell_2 = self.data.create_limit_order("Sell", self.symbol, quantity=arr_l, price=zone_150, tp=0, sl=0)
                sell_3 = self.data.create_limit_order("Sell", self.symbol, quantity=2*arr_l, price=zone_150+2*delta, tp=0, sl=(zone_150+2*delta)+round((zone_150-zone_100)/2, 2))
                sell_list = [sell_1[0]['result']['order_id'], sell_2[0]['result']['order_id'],
                             sell_3[0]['result']['order_id']]
                return buy_list, sell_list, check_levels
            else:
                print(f'Shorts not found! POC:{POC}, price:{price}')
                logger.info(f'Shorts not found! POC:{POC}, price:{price}')
                check_levels = 1
                return None, None, check_levels

    def create_2_orders(self, arr_l, _zone_150, _zone_100, _zone_75, _zone_50, _zone_25, zone_150, zone_100,
                        zone_75, zone_50, zone_25, price, POC):

        logger.info(f'Start creating orders with: {arr_l}, {_zone_150}, {_zone_100}, {_zone_75}, {_zone_50}, {_zone_25}, {zone_150}, {zone_100}, {zone_75}, {zone_50}, {zone_25}, {price}, {POC}')

        delta = 25
        check_levels = 0

        if check_levels == 0:
            if price > _zone_25:
                self.data.create_limit_order("Buy", self.symbol, arr_l, _zone_25, tp=POC,
                                             sl=_zone_25 - delta)
            elif price > _zone_50:
                self.data.create_limit_order("Buy", self.symbol, arr_l, _zone_50, tp=_zone_25,
                                             sl=_zone_50 - delta)
            elif price > _zone_75:
                self.data.create_limit_order("Buy", self.symbol, arr_l, _zone_75, tp=_zone_50,
                                             sl=_zone_75 - delta)
            elif price > _zone_100:
                self.data.create_limit_order("Buy", self.symbol, arr_l, _zone_100, tp=_zone_75,
                                             sl=_zone_100 - delta)
            elif price > _zone_150:
                self.data.create_limit_order("Buy", self.symbol, arr_l, _zone_150, tp=_zone_100,
                                             sl=_zone_150 - delta)
            else:
                print(f'Longs not found! POC:{POC}, price:{price}')
                logger.info(f'Longs not found! POC:{POC}, price:{price}')
                check_levels = 1
                return check_levels

        if check_levels == 0:
            if price < zone_25:
                self.data.create_limit_order("Sell", self.symbol, arr_l, zone_25, tp=POC,
                                             sl=zone_25 + delta)
            elif price < zone_50:
                self.data.create_limit_order("Sell", self.symbol, arr_l, zone_50, tp=zone_25,
                                             sl=zone_50 + delta)
            elif price < zone_75:
                self.data.create_limit_order("Sell", self.symbol, arr_l, zone_75, tp=zone_50,
                                             sl=zone_75 + delta)
            elif price < zone_100:
                self.data.create_limit_order("Sell", self.symbol, arr_l, zone_100, tp=zone_75,
                                             sl=zone_100 + delta)
            elif price < zone_150:
                self.data.create_limit_order("Sell", self.symbol, arr_l, zone_150, tp=zone_100,
                                             sl=zone_150 + delta)
            else:
                print(f'Shorts not found! POC:{POC}, price:{price}')
                logger.info(f'Shorts not found! POC:{POC}, price:{price}')
                check_levels = 1
                return check_levels

    def draw_zones(self, interval, limit):
        price = self.data.show_last_price()
        data_kline = Strategy.get_kline(self, interval=interval, limit=limit)

        if data_kline is None:
            print("No data received")
            logger.info("No data received")
            return 0

        _zone_150, _zone_100, _zone_75, _zone_50, _zone_25, zone_150, zone_100, \
        zone_75, zone_50, zone_25, df, POC = Strategy.get_margin_poc(data_kline)

        found_zone_150 = found_zone_100 = found_zone_75 = found_zone_50 = found_zone_25 = found_zone_150_ = found_zone_100_ = found_zone_75_ = found_zone_50_ = found_zone_25_ = 'Not found'

        if price > _zone_150:
            found_zone_150 = 'Found'
        if price > _zone_100:
            found_zone_100 = 'Found'
        if price > _zone_75:
            found_zone_75 = 'Found'
        if price > _zone_50:
            found_zone_50 = 'Found'
        if price > _zone_25:
            found_zone_25 = 'Found'

        if price < zone_150:
            found_zone_150_ = 'Found'
        if price < zone_100:
            found_zone_100_ = 'Found'
        if price < zone_75:
            found_zone_75_ = 'Found'
        if price < zone_50:
            found_zone_50_ = 'Found'
        if price < zone_25:
            found_zone_25_ = 'Found'

        return _zone_100, _zone_75, _zone_50, _zone_25, zone_100, _zone_150, zone_150, zone_100, \
               zone_75, zone_50, zone_25, df, POC, price, found_zone_150, found_zone_100, found_zone_75, found_zone_50, \
               found_zone_25, found_zone_150_, found_zone_100_, found_zone_75_, found_zone_50_, found_zone_25_

    @staticmethod
    def count_contracts(price, available_balance, leverage, percent):
        fees = 1 - (0.00075 * 2)
        return int(price * available_balance * leverage * percent / 100 * fees)

    @staticmethod
    def margin():
        try:
            csv_url = requests.get(
                'https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv?sortField=exchange&sortAsc=true&clearingCode=BTC&sector=EQUITY%20INDEX&exchange=CME',
                timeout=10,
                headers={'User-Agent': 'some cool user-agent'})
        except requests.exceptions.RequestException as e:
            path = pathlib.Path('margin.csv')
            if path.exists() and path.is_file():
                with open('margin.csv') as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',')
                    for c, row in enumerate(spamreader):
                        if c == 1:
                            return int(row[6])
            else:
                print(f'path.exists():{path.exists()}, path.is_file():{path.is_file()}, {e}')
                logger.error(f'path.exists():{path.exists()}, path.is_file():{path.is_file()}, {e}')
                raise SystemExit(e)
        else:
            url_content = csv_url.content
            csv_file = open('margin.csv', 'wb')

            csv_file.write(url_content)
            csv_file.close()

            with open('margin.csv') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                for c, row in enumerate(spamreader):
                    if c == 1:
                        return int(row[6])

    @staticmethod
    def get_margin_poc(data):
        candle = []

        for el in data[0]['result']:
            candle.append(el)

        df = pd.DataFrame(candle)
        drop_list = ['open', 'high', 'low', 'close', 'volume']
        df = df.drop(df.columns.difference(drop_list), axis=1)
        df = df.astype(np.float64)

        x = np.linspace(df.close.min(), df.close.max(), len(df))
        kde_factor = 0.1

        try:
            kde = stats.gaussian_kde(df.close)
            kdy = kde(x)
            min_prom = kdy.max() * kde_factor
            peaks, peak_props = signal.find_peaks(kdy, prominence=min_prom)
            pkx = x[peaks]
            pky = kdy[peaks]
            result = np.where(pky == pky.max())

        except Exception as e:
            print(e)
            logger.exception(f"{e}", exc_info=True)

        else:
            ind = result[0]
            POC = int(pkx[ind])
            cme_margin = Strategy.margin()
            base_zone = int(cme_margin / 25 / 2)

            # BUY ZONES
            _zone_25 = int(POC - base_zone * 0.25)
            _zone_50 = int(POC - base_zone * 0.5)
            _zone_75 = int(POC - base_zone * 0.75)
            _zone_100 = POC - base_zone
            _zone_150 = int(POC - base_zone * 1.5)

            # SELL ZONES
            zone_25 = int(POC + base_zone * 0.25)
            zone_50 = int(POC + base_zone * 0.5)
            zone_75 = int(POC + base_zone * 0.75)
            zone_100 = POC + base_zone
            zone_150 = int(POC + base_zone * 1.5)

            return _zone_150, _zone_100, _zone_75, _zone_50, _zone_25, zone_150, zone_100, \
                   zone_75, zone_50, zone_25, df, POC
