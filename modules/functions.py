import pprint
from decimal import Decimal
from modules.exceptions import *
from datetime import datetime
from termcolor import colored


class Endpoints:
    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol

    ''''
    SHOW INFO
    '''

    @exx
    def show_data_obj(self):
        return self.client.Positions.Positions_myPosition(symbol=self.symbol).result()[0]

    @exx
    def set_leverage(self, leverage):
        return self.client.Positions.Positions_saveLeverage(symbol="BTCUSD", leverage=str(leverage)).result()

    @exx
    def timer(self, timeframe, limit):
        candle_open_time = 0
        time_now_int = int(float(self.client.Common.Common_getTime().result()[0]["time_now"]))
        time_now_int_minus = time_now_int - timeframe * 60 * limit

        result = self.client.Kline.Kline_get(symbol=self.symbol, interval=str(timeframe),
                                             **{'from': time_now_int_minus},
                                             limit=limit).result()

        if result[0]['ret_msg'] == 'OK':
            while candle_open_time == 0:
                sleep(1)
                try:
                    candle_open_time = result[0]['result'][0]['open_time']
                except IndexError:
                    result = self.client.Kline.Kline_get(symbol=self.symbol, interval=str(timeframe),
                                                         **{'from': time_now_int_minus},
                                                         limit=limit).result()
        else:
            logger.exception(f"timer err:{result[0]['ret_msg']}")

        time_now_int = int(float(self.client.Common.Common_getTime().result()[0]["time_now"]))
        open_time_fix = datetime.utcfromtimestamp(int(candle_open_time)).strftime('%H:%M:%S')

        while time_now_int < candle_open_time + 60 * timeframe:
            try:
                time_now_int += 1
                time_now = datetime.utcfromtimestamp(time_now_int).strftime('%H:%M:%S')
                sleep(1)
                print(
                    f"\rtime_now: {time_now}, "
                    f"candle_open_time: {open_time_fix}",
                    end='')
            except Exception as e:
                logger.exception(f'timer timeout:{time_now_int}, {e}')

    @staticmethod
    @exx
    def count_contracts(price, available_balance, leverage, percent):
        print('counting contracts..')
        print(price, available_balance, leverage, percent)
        fees = 1 - (0.00075 * 2)
        print(f"fees:{fees}")
        print(f"contracts:{int(price * available_balance * leverage * percent * fees)}")
        logger.info(f"counting contracts..\nfees:{fees}\ncontracts:{int(price * available_balance * leverage * percent * fees)}")
        return int(price * available_balance * leverage * percent * fees)

    @exx
    def show_pnl(self):
        return round(Decimal(
            self.client.Positions.Positions_myPosition(symbol=self.symbol).result()[0]['result']['unrealised_pnl']), 10)

    @exx
    def show_order_status(self):
        return self.client.Order.Order_getOrders(symbol=self.symbol).result()[0]['result']['data'][0]['order_status']

    @exx
    def show_order_side(self):
        return self.client.Positions.Positions_myPosition(symbol=self.symbol).result()[0]['result']['side']

    @exx
    def show_last_price(self):
        return float(self.client.Market.Market_symbolInfo(symbol=self.symbol).result()[0]['result'][0]['last_price'])

    ''''
    CREATING ORDERS
    '''

    @exx
    def create_market_order(self, side, price, symbol, quantity, sl, tp):
        if side == 'Buy':
            return self.client.Order.Order_new(side=side, symbol=symbol, price=price, order_type="Market", qty=quantity,
                                               time_in_force="GoodTillCancel", stop_loss=sl, take_profit=tp).result()
        elif side == 'Sell':
            return self.client.Order.Order_new(side=side, symbol=symbol, price=price, order_type="Market", qty=quantity,
                                               time_in_force="GoodTillCancel", stop_loss=sl, take_profit=tp).result()

    @exx
    def create_close_order(self, side, symbol, quantity, price, tp):
        try:
            close_order = self.client.Conditional.Conditional_new(order_type="Limit", side=side,
                                                                  symbol=symbol, qty=str(quantity), price=str(price),
                                                                  base_price=str(tp), stop_px=str(tp),
                                                                  time_in_force="GoodTillCancel",
                                                                  close_on_trigger=True).result()
            if close_order[0]['result'] is None:
                pprint.pprint(close_order[0]['ret_code'])
                print('close_order  is None!')
                return False
            return close_order
        except TypeError as err:
            print(f"close_limit_order:{err}")
            return False

    @exx
    def create_limit_order(self, side, symbol, quantity, price, tp, sl):
        try:
            order = self.client.Order.Order_new(side=side, symbol=symbol, order_type="Limit",
                                                qty=str(quantity), price=price, take_profit=tp, stop_loss=sl,
                                                time_in_force="GoodTillCancel").result()
        except TypeError as err:
            print(f"create_limit_order - TypeError:{err}")
            logger.exception(f"create_limit_order - TypeError:{err}", exc_info=True)
            return False
        except Exception as err:
            print(f"{repr(err)}, {err}")
            logger.exception(f"{repr(err)}, {err}", exc_info=True)
        else:
            if order[0]['result'] is None:
                print('result created order is None!')
                pprint.pprint(order)
                logger.info('result created order is None!')
                logger.info(f"{order}")
                return False
            if order[0]['result'] is not None:
                result_code = order[0]['ret_code']
                if result_code == 0:
                    result_side = order[0]['result']['side']
                    if result_side == "Buy":
                        print(
                            f"Order limit {colored(result_side, 'green')} with id {order[0]['result']['order_id']}, price:{price}$")
                        logger.info(f"Order limit {result_side} with id {order[0]['result']['order_id']}, price:{price}$")
                    else:
                        print(
                            f"Order limit {colored(result_side, 'red')} with id {order[0]['result']['order_id']}, price:{price}$")
                        logger.info(
                            f"Order limit {result_side} with id {order[0]['result']['order_id']}, price:{price}$")
                    return order
                else:
                    print(f"Order limit Error with code: {result_code}!")
                    logger.error(f"Order limit Error with code: {result_code}!")
                    return False

    @exx
    def create_conditional_order(self, order_type, side, symbol, qty, base_price, stop_px, time_in_force):
        return self.client.Conditional.Conditional_new(order_type=order_type, side=side, symbol=symbol, qty=qty,
                                                       base_price=base_price, stop_px=stop_px,
                                                       time_in_force=time_in_force).result()[0]['result'][
            "stop_order_id"]

    @exx
    def cancel_orders(self):
        result = self.client.Order.Order_cancelAll(symbol=self.symbol).result()
        result_code = result[0]['ret_code']

        if result_code == 0:
            print('All orders cancelled successfully!')
            logger.info('All orders cancelled successfully!')
        else:
            logger.error(f"Error with code: {result_code}!")
            return print(f"Error with code: {result_code}!")

        return result

    ''''
    POSITION
    '''

    @exx
    def available_balance(self):
        if self.client.Wallet.Wallet_getBalance(coin="BTC").result()[0]['ret_msg'] == 'OK':
            return self.client.Wallet.Wallet_getBalance(coin="BTC").result()[0]['result']['BTC']['wallet_balance']
        else:
            return 'error! ret_code:' + str(self.client.Wallet.Wallet_getBalance(coin="BTC").result()[0]['ret_code'])

    @exx
    def position_tp(self):
        return self.client.Positions.Positions_myPosition(symbol=self.symbol).result()[0]['result']['take_profit']

    @exx
    def position_sl(self):
        return self.client.Positions.Positions_myPosition(symbol=self.symbol).result()[0]['result']['stop_loss']
