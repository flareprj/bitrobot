import pprint
from unittest import TestCase

from numpy import array
from scipy import stats, signal
from modules.strategy import Strategy
import pandas as pd
import numpy as np


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

    except ValueError as e:
        print(f'Value error: {e}')

    except Exception as e:
        print(e)
        #logger.exception(f"{e}", exc_info=True)

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


class GetPoc(TestCase):
    def setUp(self) -> None:
        self.radio = True
        self.api_key = ''
        self.api_secret = ''
        self.bot = Strategy(self.radio, "BTCUSD", self.api_key, self.api_secret, app=None)

    def test_getpoc(self):
        data_kline = Strategy.get_kline(self.bot, interval='W', limit=3)

        if data_kline is None:
            print("No data received")
            return 0

        res = Strategy.get_margin_poc(
            data_kline)

        if res is not None:
            _zone_150, _zone_100, _zone_75, _zone_50, _zone_25, zone_150, zone_100, \
            zone_75, zone_50, zone_25, df, POC = res
        else:
            while res is None:
                print('waiting for trading data..')
                res = Strategy.get_margin_poc(
                    data_kline)
            else:
                print('data received, continue trade..')




