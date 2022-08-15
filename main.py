import http.client
import sys
import keyboard

from pybit.inverse_perpetual import HTTP
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtCore import pyqtSlot, QThreadPool, QSettings
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QApplication,
    QDialog
)
from gui.qt6 import Ui_MainWindow
from gui.about import Ui_Dialog

from modules.strategy import *


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

    def update_figure(self):
        self.axes.cla()


class About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.d = Ui_Dialog()
        self.d.setupUi(self)
        self.d.pushButton.clicked.connect(lambda: self.close())


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.sell_list = None
        self.buy_list = None
        self.is_orders = None
        self.status = None
        self.timer = None
        self.trailing_stop = None
        self.POC = None
        self.price = None
        self.zone_25 = None
        self.zone_50 = None
        self.zone_75 = None
        self.zone_100 = None
        self.zone_150 = None
        self._zone_25 = None
        self._zone_50 = None
        self._zone_75 = None
        self._zone_100 = None
        self._zone_150 = None
        self.bot = None
        self.session = None
        self.limit = None
        self.interval = None
        self.balance = None
        self.leverage = None
        self.percents = None
        self.api_key = None
        self.api_secret = None
        self.radio = None
        self.w1 = self.w2 = self.w3 = self.w4 = self.w5 = None
        self.order_weights = [10, 0, 0, 0, 0]
        self.arr_l = self.arr_s = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.canvas = MplCanvas(self, width=5, height=3, dpi=100)
        lay = QVBoxLayout(self.ui.plotwidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.canvas)

        self.full_version = True

        if self.full_version:
            self.ui.test_rb.setEnabled(True)
            self.ui.main_rb.setEnabled(True)
            self.ui.main_rb.setChecked(True)
        else:
            self.ui.test_rb.setEnabled(True)
            self.ui.main_rb.setEnabled(False)
            self.ui.test_rb.setChecked(True)
            self.ui.checkAuto.setEnabled(False)

        self.is_alive = False
        self.settings = QSettings('Flareprj', 'BitRobot')
        self.load_settings()
        self.thread_manager = QThreadPool()

        self.ui.startButton.clicked.connect(self.get_data_init)
        self.ui.stopButton.clicked.connect(self.stop_process)
        self.ui.createButton.clicked.connect(self.create)
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.resetButton.clicked.connect(self.reset)
        self.ui.checkAuto.clicked.connect(self.disable_areas)

        self.ui.actionExit.triggered.connect(lambda: QApplication.quit())
        self.ui.actionAbout.triggered.connect(self.about)

    def load_settings(self):
        if self.settings.contains("api_key"):
            self.ui.api_key.setText(self.settings.value("api_key"))
        if self.settings.contains("api_secret"):
            self.ui.api_secret.setText(self.settings.value("api_secret"))
        if self.settings.contains("lineEdit_3"):
            self.ui.lineEdit_3.setText(self.settings.value("lineEdit_3"))
        if self.settings.contains("lineEdit_4"):
            self.ui.lineEdit_4.setText(self.settings.value("lineEdit_4"))
        if self.settings.contains("lineEdit_5"):
            self.ui.lineEdit_5.setText(self.settings.value("lineEdit_5"))
        if self.settings.contains("lineEdit_6"):
            self.ui.lineEdit_6.setText(self.settings.value("lineEdit_6"))
        if self.settings.contains("trailing_stop"):
            self.ui.trailing_stop.setText(self.settings.value("trailing_stop"))
        if self.settings.contains("timer"):
            self.ui.timer.setText(self.settings.value("timer"))
        if self.settings.contains("w1"):
            self.ui.w1.setText(self.settings.value("w1"))
        if self.settings.contains("w2"):
            self.ui.w2.setText(self.settings.value("w2"))
        if self.settings.contains("w3"):
            self.ui.w3.setText(self.settings.value("w3"))
        if self.settings.contains("w4"):
            self.ui.w4.setText(self.settings.value("w4"))
        if self.settings.contains("w5"):
            self.ui.w5.setText(self.settings.value("w5"))

        if self.settings.contains("test_rb"):
            self.ui.test_rb.setChecked(self.settings.value("test_rb", False, bool))
        if self.settings.contains("main_rb"):
            self.ui.main_rb.setChecked(self.settings.value("main_rb", True, bool))
        if self.settings.contains("checkAuto"):
            self.ui.checkAuto.setChecked(self.settings.value("checkAuto", True, bool))
        if self.settings.contains("multorders"):
            self.ui.multorders.setChecked(self.settings.value("multorders", True, bool))

    def save_settings(self):
        self.settings.setValue("api_key", self.ui.api_key.text())
        self.settings.setValue("api_secret", self.ui.api_secret.text())
        self.settings.setValue("lineEdit_3", self.ui.lineEdit_3.text())
        self.settings.setValue("lineEdit_4", self.ui.lineEdit_4.text())
        self.settings.setValue("lineEdit_5", self.ui.lineEdit_5.text())
        self.settings.setValue("lineEdit_6", self.ui.lineEdit_6.text())
        self.settings.setValue("trailing_stop", self.ui.trailing_stop.text())
        self.settings.setValue("timer", self.ui.timer.text())
        self.settings.setValue("w1", self.ui.w1.text())
        self.settings.setValue("w2", self.ui.w2.text())
        self.settings.setValue("w3", self.ui.w3.text())
        self.settings.setValue("w4", self.ui.w4.text())
        self.settings.setValue("w5", self.ui.w5.text())

        self.settings.setValue("test_rb", self.ui.test_rb.isChecked())
        self.settings.setValue("main_rb", self.ui.main_rb.isChecked())
        self.settings.setValue("checkAuto", self.ui.checkAuto.isChecked())
        self.settings.setValue("multorders", self.ui.checkAuto.isChecked())

    def closeEvent(self, event) -> None:
        self.save_settings()

    def about(self):
        dlg = About(self)
        dlg.exec()

    def update_scrollbar(self):
        verScrollBar = self.ui.textBrowser.verticalScrollBar()
        scrollIsAtEnd = verScrollBar.maximum() - verScrollBar.value() >= 10
        if scrollIsAtEnd:
            verScrollBar.setValue(verScrollBar.maximum())

    @pyqtSlot()
    def disable_areas(self):
        if not self.ui.checkAuto.isChecked():
            if self.ui.trailing_stop.text() == '':
                self.ui.trailing_stop.setText('50')
            if self.ui.timer.text() == '':
                self.ui.timer.setText('500')
            self.ui.trailing_stop.setEnabled(False)
            self.ui.timer.setEnabled(False)
            self.ui.multorders.setEnabled(False)
            self.ui.multorders.setChecked(False)
            self.reset()
        else:
            self.ui.trailing_stop.setEnabled(True)
            self.ui.multorders.setEnabled(True)
            self.ui.timer.setEnabled(True)
            self.reset()

    @pyqtSlot()
    def reset(self):
        if not self.ui.checkAuto.isChecked():
            self.ui.w1.setText('10')
            self.ui.w2.setText('19')
            self.ui.w3.setText('30')
            self.ui.w4.setText('45')
            self.ui.w5.setText('100')
        else:
            self.ui.w1.setText('10')
            self.ui.w2.setText('0')
            self.ui.w3.setText('0')
            self.ui.w4.setText('0')
            self.ui.w5.setText('0')

    @pyqtSlot()
    def get_data_init(self):
        self.api_key = self.ui.api_key.text()
        self.api_secret = self.ui.api_secret.text()

        if self.api_key == '' or self.api_secret == '':
            self.ui.textBrowser.append(f"Api keys is empty")
            return

        if self.ui.test_rb.isChecked():
            self.radio = True
        else:
            self.radio = False

        list_tf_main = ['1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M']
        list_tf_test = ['D', 'W', 'M']

        check_tf = self.ui.lineEdit_3.text()
        check_limit = self.ui.lineEdit_4.text()

        if not self.full_version:
            if self.radio:
                if check_tf not in list_tf_test:
                    self.ui.textBrowser.append(
                        f"Incorrect timeframe - available timeframes for test account - 'D', 'W', 'M'")
                    return
        else:
            if check_tf not in list_tf_main:
                self.ui.textBrowser.append(
                    f"Incorrect timeframe")
                return

        try:
            check_limit = int(check_limit)
        except ValueError as e:
            self.ui.textBrowser.append(f"Candle limit value error! {e}")
            return
        else:
            if check_limit > 200 or check_limit < 5:
                self.ui.textBrowser.append(f"The number of candles must be 5-200")
                return

        try:
            int(self.ui.lineEdit_5.text())
            int(self.ui.lineEdit_4.text())
            round(float(self.ui.lineEdit_6.text()), 2)
            int(self.ui.trailing_stop.text())
            int(self.ui.timer.text())
            round(float(self.ui.w1.text()), 2)
            round(float(self.ui.w2.text()), 2)
            round(float(self.ui.w3.text()), 2)
            round(float(self.ui.w4.text()), 2)
            round(float(self.ui.w5.text()), 2)
        except ValueError as e:
            self.ui.textBrowser.append(f"Value error:{e}")
            return
        else:
            self.ui.startButton.setEnabled(False)

        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"Start.. time:{datetime.now()}")
        print(f"Start..TF:{self.ui.lineEdit_3.text()}, CS:{self.ui.lineEdit_4.text()}, LE:{self.ui.lineEdit_5.text()}, "
              f"AA:{self.ui.lineEdit_6.text()}, TS:{self.ui.trailing_stop.text()}, TR:{self.ui.timer.text()}, time:{datetime.now()}")
        logger.info(f"Start..TF:{self.ui.lineEdit_3.text()}, CS:{self.ui.lineEdit_4.text()}, LE:{self.ui.lineEdit_5.text()}, "
              f"AA:{self.ui.lineEdit_6.text()}, TS:{self.ui.trailing_stop.text()}, TR:{self.ui.timer.text()}")

        self.ui.textBrowser.append('connecting..')
        self.bot = Strategy(self.radio, "BTCUSD", self.api_key, self.api_secret, MainWindow)

        if self.radio:
            self.session = HTTP("https://api-testnet.bybit.com", api_key=self.api_key,
                                api_secret=self.api_secret)
        else:
            self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                                api_secret=self.api_secret)

        self.ui.textBrowser.append(f"get available balance..")
        self.balance = self.bot.data.available_balance()
        self.leverage = int(self.ui.lineEdit_5.text())

        if isinstance(self.balance, str):
            self.ui.textBrowser.append(self.balance)
            return

        if self.balance is not None and self.balance > 0:
            self.ui.textBrowser.append('balance: ' + str(self.balance) + ' BTC')
            self.interval = self.ui.lineEdit_3.text()
            self.limit = int(self.ui.lineEdit_4.text())
            self.percents = round(float(self.ui.lineEdit_6.text()), 2)
            self.w1 = round(float(self.ui.w1.text()), 2)
            self.w2 = round(float(self.ui.w2.text()), 2)
            self.w3 = round(float(self.ui.w3.text()), 2)
            self.w4 = round(float(self.ui.w4.text()), 2)
            self.w5 = round(float(self.ui.w5.text()), 2)
            self.order_weights = [self.w1, self.w2, self.w3, self.w4, self.w5]
            self.trailing_stop = int(self.ui.trailing_stop.text())
            self.timer = int(self.ui.timer.text())
        else:
            if self.balance == 0:
                self.ui.textBrowser.append('Add money to your balance!')
                return
            else:
                self.ui.textBrowser.append(self.balance)
                return

        self.cancel()

        self.is_alive = True
        if self.is_alive:
            self.thread_manager.start(self.get_data)

    @pyqtSlot()
    def get_data(self):
        if self.is_alive:
            # Auto
            if self.ui.checkAuto.isChecked() and not self.ui.multorders.isChecked():
                print("AUTO_MODE")
                logger.info("AUTO_MODE")
                self.ui.createButton.setEnabled(False)
                self.ui.cancelButton.setEnabled(False)

                self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
                self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw_2()

                self.arr_l.extend(self.arr_s)
                self.arr_l = [x for x in self.arr_l if x != 0]

                res = self.create_2()
                if res == 0:
                    return
                elif res == 1:
                    print('Need to find new levels, the search begins..')
                    logger.info('Need to find new levels, the search begins..')
                    self.stop_process(check_levels=1)
                sleep_()

            # Auto + multi
            if self.ui.checkAuto.isChecked() and self.ui.multorders.isChecked():
                print("AUTO+MULTI")
                logger.info("AUTO+MULTI")
                self.ui.createButton.setEnabled(False)
                self.ui.cancelButton.setEnabled(False)

                self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
                self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw_2()

                self.arr_l.extend(self.arr_s)
                self.arr_l = [x for x in self.arr_l if x != 0]

                buy_list, sell_list, res = self.create_6()
                if res == -1:
                    return
                if res == 1:
                    print('Need to find new levels, the search begins..')
                    logger.info('Need to find new levels, the search begins..')
                    self.stop_process(check_levels=1)

                self.buy_list = buy_list
                self.sell_list = sell_list

            # Manual
            if not self.ui.checkAuto.isChecked():
                print("MANUAL")
                logger.info("MANUAL")
                self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
                self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw()

        while self.is_alive:
            # Auto
            if self.ui.checkAuto.isChecked() and not self.ui.multorders.isChecked():
                self.status = self.bot.show_order_status()
                print(f'current_status: {self.status}')
                logger.info(f'current_status: {self.status}')
                if self.status == "New":
                    print('the levels found!')
                    self.ui.textBrowser.append('the levels found!')
                    logger.info('the levels found!')
                    while self.status == "New":
                        elapsed_time = self.timer
                        while elapsed_time > 0 and self.status == "New":
                            try:
                                self.status = self.bot.show_order_status()
                                if self.status is None:
                                    while self.status is None:
                                        self.status = self.bot.show_order_status()
                                        print(f'current_status: {self.status}, try again..')
                                        logger.info(f'current_status: {self.status}, try again..')
                                        sleep_()
                                live_price = self.bot.get_live_price() + '$'
                                live_pnl = '0 BTC'
                                self.ui.label_12.setText(live_price)
                                self.ui.label_15.setText(live_pnl)
                                if self.status == "Untriggered" or not self.is_alive:
                                    break
                                print(f"\relapsed_time: {elapsed_time}sec", end='')
                                live_elapsed = str(elapsed_time) + " sec"
                                self.ui.label_22.setText(live_elapsed)
                                elapsed_time -= 1
                                sleep_()
                            except Exception as e:
                                print('\n', e)
                                logger.exception(f'{e}', exc_info=True)
                        else:
                            print(f'\ntimer finished! status:{self.status}')
                            logger.info(f'timer finished! status:{self.status}')
                            if self.is_alive:
                                self.update_redraw()
                            else:
                                print(f"Stop receiving the data, time:{datetime.now()}")
                                logger.info(f"Stop receiving the data")
                                break

                elif self.status == "Untriggered":
                    print("We have Untriggered order! Cancel another orders!")
                    logger.info(f"We have Untriggered order! Cancel another orders!")
                    self.cancel()
                    try:
                        order_id = self.session.get_active_order(
                            symbol="BTCUSD",
                            order_status="Untriggered"
                        )['result']['data'][0]['order_id']
                    except IndexError as e:
                        print(e)
                        logger.exception(e, exc_info=True)
                        sleep_()
                        continue
                    except Exception as e:
                        print(e)
                        logger.exception(e, exc_info=True)
                        sleep_()
                        continue
                    else:
                        print(f"untriggered_order_id:{order_id}")
                        logger.info(f"untriggered_order_id:{order_id}")
                        while self.status == "Untriggered":
                            try:
                                req_pos = self.session.my_position(symbol="BTCUSD")['result']
                                take_profit = float(req_pos['take_profit'])
                                entry_price = float(req_pos['entry_price'])
                                side = req_pos['side']
                                size = req_pos['size']
                                sl_change = 0

                                print(f"take_profit: {take_profit}")
                                print(f"entry_price: {entry_price}")
                                print(f"side: {side}")
                                logger.info(
                                    f"take_profit:{take_profit}, entry_price:{entry_price}, side:{side}")
                            except http.client.RemoteDisconnected as e:
                                print(repr(e), e)
                                logger.error(f"RemoteDisconnected, {e}")
                                sleep_()
                            except requests.exceptions.ConnectionError as e:
                                print(repr(e), e)
                                logger.exception(e, exc_info=True)
                                sleep_()
                            except Exception as e:
                                print(repr(e), e)
                                logger.exception(e, exc_info=True)
                                sleep_()
                            else:
                                if take_profit > entry_price:
                                    trigger_trailing = int(entry_price + ((take_profit - entry_price) / 2))
                                    print(f"trigger_trailing: {trigger_trailing}$")
                                    logger.info(f"trigger_trailing: {trigger_trailing}$")
                                elif take_profit < entry_price:
                                    trigger_trailing = int(entry_price - abs((take_profit - entry_price) / 2))
                                    print(f"trigger_trailing: {trigger_trailing}$")
                                    logger.info(f"trigger_trailing: {trigger_trailing}$")
                                else:
                                    break

                                if size != 0 and size is not None:
                                    try:
                                        self.session.set_trading_stop(symbol="BTCUSD", take_profit=0,
                                                                      trailing_stop=self.trailing_stop,
                                                                      new_trailing_active=trigger_trailing)
                                    except Exception as e:
                                        print(e)
                                        logger.exception(f"{e}", exc_info=True)
                                        sleep_()
                                    else:
                                        try:
                                            req_2 = self.session.my_position(symbol="BTCUSD")
                                        except Exception as e:
                                            print(e)
                                            logger.exception(f"{e}", exc_info=True)
                                            sleep_()
                                        else:
                                            if float(req_2['result']['trailing_stop']) != '0':
                                                print(
                                                    f"placing a trailing-stop: {trigger_trailing}$ - ok! time:{datetime.now()}")
                                                logger.info(f"placing a trailing-stop: {trigger_trailing}$ - ok!")
                                                logger.info(f"rate_limit_status: {req_2['rate_limit_status']}")
                                                logger.info(f"rate_limit_reset_ms: {req_2['rate_limit_reset_ms']}")
                                                logger.info(f"rate_limit: {req_2['rate_limit']}")
                                            else:
                                                print(f"error when placing a trailing-stop! time:{datetime.now()}")
                                                logger.info(f"error when placing a trailing-stop!")

                                while self.status == "Untriggered":
                                    try:
                                        self.status = self.bot.show_order_status()
                                        price = self.bot.get_live_price()
                                        live_price = price + '$'
                                        live_pnl = str(self.bot.get_live_pnl()) + ' BTC'
                                        self.ui.label_12.setText(live_price)
                                        self.ui.label_15.setText(live_pnl)

                                        delta_breakeven = 25

                                        if side == "Buy" and float(price) > float(trigger_trailing-int(self.ui.trailing_stop.text()))+delta_breakeven and sl_change == 0:
                                            try:
                                                res = self.session.set_trading_stop(symbol="BTCUSD", stop_loss=int(entry_price+((trigger_trailing-entry_price)/2)))
                                                if res['ret_code'] == 0:
                                                    print(f'\nSL has been replaced! New price:{res["result"]["stop_loss"]}$')
                                                    logger.info(f'SL has been replaced! New price:{res["result"]["stop_loss"]}$')
                                                    sl_change = 1
                                            except Exception as e:
                                                print(e)
                                        if side == "Sell" and float(price) < float(trigger_trailing+int(self.ui.trailing_stop.text()))-delta_breakeven and sl_change == 0:
                                            try:
                                                res = self.session.set_trading_stop(symbol="BTCUSD", stop_loss=int(entry_price-((entry_price-trigger_trailing)/2)))
                                                if res['ret_code'] == 0:
                                                    print(f'\nSL has been replaced! New price: {res["result"]["stop_loss"]}$')
                                                    logger.info(f'SL has been replaced! New price: {res["result"]["stop_loss"]}$')
                                                    sl_change = 1
                                            except Exception as e:
                                                print(e)

                                        print(f"\r{live_pnl}, entry_price:{round(entry_price, 2)}$", end='')
                                        sleep(1)
                                        if self.status != "Untriggered":
                                            logger.info(f"IF BLOCK, {self.status}")
                                            break
                                    except http.client.RemoteDisconnected as e:
                                        logger.error(f"RemoteDisconnected, {e}")
                                        sleep_()
                                    except Exception as e:
                                        print(e)
                                        logger.exception(e, exc_info=True)
                                        sleep_()

                        print(f'\nStop-Take Order was executed! time:{datetime.now()}')
                        logger.info(f'Stop-Take Order was executed!')
                        self.update_redraw()
                        self.status = self.bot.show_order_status()

                elif not self.is_alive:
                    break
                else:
                    print(f'\nStrange situation! status:{self.status}, time:{datetime.now()}')
                    logger.info(f'Strange situation! status:{self.status}')
                    self.update_redraw()

            # Auto + multi
            if self.ui.checkAuto.isChecked() and self.ui.multorders.isChecked():
                self.is_orders = True
                self.sl_change = False

                position_size = self.session.my_position(symbol="BTCUSD")['result']['size']

                while position_size == 0:
                    position_size = self.session.my_position(symbol="BTCUSD")['result']['size']
                    elapsed_time = self.timer
                    if not self.is_alive:
                        break
                    while elapsed_time > 0 and position_size == 0:
                        try:
                            position_size = self.session.my_position(symbol="BTCUSD")['result']['size']
                            live_elapsed = str(elapsed_time) + " sec"
                            self.ui.label_22.setText(live_elapsed)
                            elapsed_time -= 1
                            print(f"\r{elapsed_time} sec", end='')
                            if not self.is_alive:
                                break
                            sleep(1)
                        except Exception as e:
                            print('\n', e)
                            logger.exception(f'{e}', exc_info=True)
                    else:
                        print(f'\ntimer finished!')
                        logger.info(f'timer finished!')
                        if self.is_alive and position_size == 0:
                            print(f'updating order list: {self.is_alive}, {position_size}')
                            logger.info(f'updating order list: {self.is_alive}, {position_size}')
                            self.update_order_list()
                        if not self.is_alive:
                            print(f"Stop receiving the data, time:{datetime.now()}")
                            logger.info(f"Stop receiving the data")
                            break
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
                        logger.info(
                            f"take_profit:{take_profit}, entry_price:{entry_price}, side:{side}")
                        print(side, self.buy_list, self.sell_list)
                        self.cancel_orders_list(side, self.buy_list, self.sell_list)
                        logger.info(f"cancel_orders_list: {side}, {self.buy_list}, {self.sell_list}")

                        if side == "Buy":
                            distance = int(entry_price + ((take_profit - entry_price) / 2))
                        elif side == "Sell":
                            distance = int(entry_price - ((entry_price - take_profit) / 2))

                        while position_size != 0:
                            try:
                                count_active_orders = len(self.session.get_active_order(symbol="BTCUSD", order_status="New")['result']['data'])
                                position = self.session.my_position(symbol="BTCUSD")['result']
                                position_size = position['size']
                                entry_price = round(float(position['entry_price']), 2)
                                price = self.bot.get_live_price()
                                pnl = self.bot.get_live_pnl()

                                print(f"PNL: {pnl}, size: {position_size}, active_orders: {count_active_orders}")
                                #logger.info(f"PNL: {live_pnl}, size: {position_size}, active_orders: {count_active_orders}")

                                if count_active_orders == 0 and float(pnl) < 0:
                                    code = self.filter_timer(1, 1, entry_price, side, position_size)
                                    if code == 1:
                                        self.update_order_list()
                                        break

                                self.ui.label_12.setText(price)
                                self.ui.label_15.setText(pnl)

                                delta_breakeven = 25

                                if side == "Buy" and float(price) > float(distance - 50) + delta_breakeven and not self.sl_change:
                                    print('Entering move sl BUY range!')
                                    logger.info('Entering move sl BUY range!')
                                    try:
                                        res = self.session.set_trading_stop(symbol="BTCUSD", stop_loss=int(
                                            entry_price + ((distance - entry_price) / 2)))
                                        if res['ret_code'] == 0:
                                            print(f'\nSL has been replaced! New price:{res["result"]["stop_loss"]}$')
                                            logger.info(
                                                f'SL has been replaced! New price:{res["result"]["stop_loss"]}$')
                                            self.sl_change = True
                                    except Exception as e:
                                        print(e)

                                if side == "Sell" and float(price) < float(distance + 50) - delta_breakeven and not self.sl_change:
                                    print('Entering move sl SELL range!')
                                    logger.info('Entering move sl SELL range!')
                                    try:
                                        res = self.session.set_trading_stop(symbol="BTCUSD", stop_loss=int(
                                            entry_price - ((entry_price - distance) / 2)))
                                        if res['ret_code'] == 0:
                                            print(f'\nSL has been replaced! New price: {res["result"]["stop_loss"]}$')
                                            logger.info(
                                                f'SL has been replaced! New price: {res["result"]["stop_loss"]}$')
                                            self.sl_change = True
                                    except Exception as e:
                                        print(e)

                                sleep(3)
                            except Exception as e:
                                print(e)
                        else:
                            print(f"Order was executed! Position size: {position_size}")
                            logger.info(f"Order was executed! Position size: {position_size}")
                            self.update_order_list()

            # Manual
            if not self.ui.checkAuto.isChecked():
                self.ui.createButton.setEnabled(True)
                self.ui.cancelButton.setEnabled(True)
                live_price = self.bot.get_live_price() + '$'
                live_pnl = str(self.bot.get_live_pnl()) + ' BTC'
                self.ui.label_12.setText(live_price)
                self.ui.label_15.setText(live_pnl)
                sleep(1)

    @pyqtSlot()
    def stop_process(self, check_levels=0):
        if self.is_alive:
            self.status = self.bot.show_order_status()

            if check_levels == 1:
                self.ui.textBrowser.append(f'finding new levels..')
                list_tf = ['1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M']
                current_tf = self.ui.lineEdit_3.text()
                for i, tf in enumerate(list_tf, start=0):
                    if tf == current_tf:
                        self.ui.lineEdit_3.setText(list_tf[i - 1])
                        self.get_data()
                        break

            if self.status == "Untriggered" or self.status == "New":
                self.cancel()
                self.is_alive = False
                self.ui.textBrowser.append(f"Stop receiving the data, time:{datetime.now()}")
                print(f"Stop receiving the data, time:{datetime.now()}")
                logger.info(f"Stop receiving the data")
                self.update_scrollbar()
                self.ui.startButton.setEnabled(True)
                return
            if not self.ui.startButton.isEnabled():
                self.ui.startButton.setEnabled(True)
                return

    def create_market(self, side, qty):
        self.session.place_active_order(
            symbol="BTCUSD",
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel"
        )

    def filter_timer(self, timeframe, limit, entry_price, side, position_size):
        try:
            time_now_int = int(float(self.session.server_time()['time_now']))
            time_now_int_minus = time_now_int - timeframe * 60 * limit

            result = self.session.query_kline(symbol='BTCUSD', interval=str(timeframe),
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
                    print(f'candle_open_time: {open_time_fix}, time_now: {time_now}')
                    logger.info(f'candle_open_time: {open_time_fix}, time_now: {time_now}')
                except Exception as e:
                    print(f'timer timeout:{time_now_int}, {e}')
            else:
                print('Candle was closed!')
                logger.info('Candle was closed!')
                last_price = round(float(self.session.latest_information_for_symbol(
                    symbol="BTCUSD"
                )['result'][0]['last_price']), 2)
                print(f'last_price: {last_price}$, entry: {entry_price}$')

                if side == 'Buy' and last_price < entry_price:
                    self.create_market(side='Sell', qty=position_size)
                    print(f'Order {side} was closed!')
                    logger.info(f'Order {side} was closed!')
                    return 1
                elif side == 'Sell' and last_price > entry_price:
                    self.create_market(side='Buy', qty=position_size)
                    print(f'Order {side} was closed!')
                    logger.info(f'Order {side} was closed!')
                    return 1
                else:
                    print('The candle closes positive, so we continue trading..')
                    logger.info('The candle closes positive, so we continue trading..')
                    return 0


    def update_redraw(self):
        self.cancel()
        print('update levels..')
        logger.info(f'update levels..')
        self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
        self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw_2()
        self.arr_l.extend(self.arr_s)
        self.arr_l = [x for x in self.arr_l if x != 0]
        print('redraw completed..')
        logger.info(f'redraw completed..')

        # открываем новые ордера только когда их нет
        try:
            qt = self.session.get_active_order(
                symbol="BTCUSD",
                order_status="New"
            )['result']
        except Exception as err:
            print(f'{err}')
            logger.exception(repr(err), exc_info=True)
        else:
            if qt is not None:
                return
        finally:
            res = self.create_2()
            if res == 0:
                return
            sleep_()
            self.status = self.bot.show_order_status()

    def update_order_list(self):
        self.cancel()
        print('update levels..')
        logger.info(f'update levels..')
        self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
        self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw_2()
        self.arr_l.extend(self.arr_s)
        self.arr_l = [x for x in self.arr_l if x != 0]
        print('redraw completed..')
        logger.info(f'redraw completed..')

        buy_list, sell_list, res = self.create_6()

        if res == -1:
            return
        if res == 1:
            print('Need to find new levels, the search begins..')
            logger.info('Need to find new levels, the search begins..')
            self.stop_process(check_levels=1)

        self.buy_list = buy_list
        self.sell_list = sell_list

    def qty_calc(self):
        _, _, qty_l, qty_s = self.bot.count_orders(self.balance, self.leverage, self.interval,
                                                   self.limit,
                                                   self.percents, self.order_weights)
        return _, _, qty_l, qty_s

    def draw(self):
        obj = Strategy(self.radio, "BTCUSD", self.api_key, self.api_secret, MainWindow)

        self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_100, self._zone_150, self.zone_150, self.zone_100, \
        self.zone_75, self.zone_50, self.zone_25, df, self.POC, self.price, found_zone_150, found_zone_100, found_zone_75, found_zone_50, \
        found_zone_25, found_zone_150_, found_zone_100_, found_zone_75_, found_zone_50_, found_zone_25_ = obj.draw_zones(
            self.interval, self.limit)

        self.canvas.update_figure()
        self.canvas.axes.plot(df.index, df.close, 'r')
        self.canvas.axes.hlines(int(self.price), 0, df.index.max(), colors='orange', linestyles='dashed')
        self.canvas.axes.hlines(self.POC, 0, df.index.max(), colors='blue', linestyles='solid')

        if self.price > self._zone_150:
            self.canvas.axes.hlines(self._zone_150, 0, df.index.max(), colors='green', linestyles='solid')
        if self.price > self._zone_100:
            self.canvas.axes.hlines(self._zone_100, 0, df.index.max(), colors='green', linestyles='solid')
        if self.price > self._zone_75:
            self.canvas.axes.hlines(self._zone_75, 0, df.index.max(), colors='green', linestyles='solid')
        if self.price > self._zone_50:
            self.canvas.axes.hlines(self._zone_50, 0, df.index.max(), colors='green', linestyles='solid')
        if self.price > self._zone_25:
            self.canvas.axes.hlines(self._zone_25, 0, df.index.max(), colors='green', linestyles='solid')

        if self.price < self.zone_150:
            self.canvas.axes.hlines(self.zone_150, 0, df.index.max(), colors='red', linestyles='solid')
        if self.price < self.zone_100:
            self.canvas.axes.hlines(self.zone_100, 0, df.index.max(), colors='red', linestyles='solid')
        if self.price < self.zone_75:
            self.canvas.axes.hlines(self.zone_75, 0, df.index.max(), colors='red', linestyles='solid')
        if self.price < self.zone_50:
            self.canvas.axes.hlines(self.zone_50, 0, df.index.max(), colors='red', linestyles='solid')
        if self.price < self.zone_25:
            self.canvas.axes.hlines(self.zone_25, 0, df.index.max(), colors='red', linestyles='solid')

        self.canvas.draw()

        _, _, qty_l, qty_s = self.bot.count_orders(self.balance, self.leverage, self.interval,
                                                   self.limit,
                                                   self.percents, self.order_weights)

        deposit = int(count_deposit(self.price, self.balance, self.leverage, self.percents))

        self.arr_l, self.arr_s = fills(deposit, qty_l, qty_s, self.order_weights)

        try:
            self.ui.w1_2.setText(str(self.arr_l[0]))
            self.ui.w2_2.setText(str(self.arr_l[1]))
            self.ui.w3_2.setText(str(self.arr_l[2]))
            self.ui.w4_2.setText(str(self.arr_l[3]))
            self.ui.w5_2.setText(str(self.arr_l[4]))

            self.ui.w1_3.setText(str(self.arr_s[0]))
            self.ui.w2_3.setText(str(self.arr_s[1]))
            self.ui.w3_3.setText(str(self.arr_s[2]))
            self.ui.w4_3.setText(str(self.arr_s[3]))
            self.ui.w5_3.setText(str(self.arr_s[4]))
        except IndexError as e:
            logger.exception(f"{e}", exc_info=True)

        self.ui.textBrowser.append(f"******LONGS******")
        self.ui.textBrowser.append(f"-150: {self._zone_150}$ --- {found_zone_150}")
        self.ui.textBrowser.append(f"-100: {self._zone_100}$ --- {found_zone_100}")
        self.ui.textBrowser.append(f"-75: {self._zone_75}$ --- {found_zone_75}")
        self.ui.textBrowser.append(f"-50: {self._zone_50}$ --- {found_zone_50}")
        self.ui.textBrowser.append(f"-25: {self._zone_25}$ --- {found_zone_25}")
        self.ui.textBrowser.append(f"{self.arr_l}")
        self.ui.textBrowser.append(f"******SHORTS******")
        self.ui.textBrowser.append(f"+150: {self.zone_150}$ --- {found_zone_150_}")
        self.ui.textBrowser.append(f"+100: {self.zone_100}$ --- {found_zone_100_}")
        self.ui.textBrowser.append(f"+75: {self.zone_75}$ --- {found_zone_75_}")
        self.ui.textBrowser.append(f"+50: {self.zone_50}$ --- {found_zone_50_}")
        self.ui.textBrowser.append(f"+25: {self.zone_25}$ --- {found_zone_25_}")
        self.ui.textBrowser.append(f"{self.arr_s}")

        self.update_scrollbar()

        self.ui.label_10.setText(str(self.POC) + '$')

        return self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
               self.zone_75, self.zone_50, self.zone_25, self.price, self.POC

    def draw_2(self):
        obj = Strategy(self.radio, "BTCUSD", self.api_key, self.api_secret, MainWindow)

        self.interval = self.ui.lineEdit_3.text()

        self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_100, self._zone_150, self.zone_150, self.zone_100, \
        self.zone_75, self.zone_50, self.zone_25, df, self.POC, self.price, found_zone_150, found_zone_100, found_zone_75, found_zone_50, \
        found_zone_25, found_zone_150_, found_zone_100_, found_zone_75_, found_zone_50_, found_zone_25_ = obj.draw_zones(
            self.interval, self.limit)

        self.canvas.update_figure()
        self.canvas.axes.plot(df.index, df.close, 'r')
        self.canvas.axes.hlines(int(self.price), 0, df.index.max(), colors='orange', linestyles='dashed')
        self.canvas.axes.hlines(self.POC, 0, df.index.max(), colors='blue', linestyles='solid')

        if self.price > self._zone_25:
            self.canvas.axes.hlines(self._zone_25, 0, df.index.max(), colors='green', linestyles='solid')
        elif self.price > self._zone_50:
            self.canvas.axes.hlines(self._zone_50, 0, df.index.max(), colors='green', linestyles='solid')
        elif self.price > self._zone_75:
            self.canvas.axes.hlines(self._zone_75, 0, df.index.max(), colors='green', linestyles='solid')
        elif self.price > self._zone_100:
            self.canvas.axes.hlines(self._zone_100, 0, df.index.max(), colors='green', linestyles='solid')
        elif self.price > self._zone_150:
            self.canvas.axes.hlines(self._zone_150, 0, df.index.max(), colors='green', linestyles='solid')

        if self.price < self.zone_25:
            self.canvas.axes.hlines(self.zone_25, 0, df.index.max(), colors='red', linestyles='solid')
        elif self.price < self.zone_50:
            self.canvas.axes.hlines(self.zone_50, 0, df.index.max(), colors='red', linestyles='solid')
        elif self.price < self.zone_75:
            self.canvas.axes.hlines(self.zone_75, 0, df.index.max(), colors='red', linestyles='solid')
        elif self.price < self.zone_100:
            self.canvas.axes.hlines(self.zone_100, 0, df.index.max(), colors='red', linestyles='solid')
        elif self.price < self.zone_150:
            self.canvas.axes.hlines(self.zone_150, 0, df.index.max(), colors='red', linestyles='solid')

        self.canvas.draw()

        self.arr_l, self.arr_s, qty_l, qty_s = self.bot.count_orders(self.balance, self.leverage, self.interval,
                                                                     self.limit,
                                                                     self.percents, self.order_weights)

        deposit = int(count_deposit(self.price, self.balance, self.leverage, self.percents))

        logger.info(f'counted deposit: {deposit}$')

        try:
            self.arr_l, self.arr_s = fills(deposit, qty_l, qty_s, self.order_weights)
            self.ui.w1_2.setText(str(self.arr_l[0]))
            self.ui.w2_2.setText(str(self.arr_l[1]))
            self.ui.w3_2.setText(str(self.arr_l[2]))
            self.ui.w4_2.setText(str(self.arr_l[3]))
            self.ui.w5_2.setText(str(self.arr_l[4]))

            self.ui.w1_3.setText(str(self.arr_s[0]))
            self.ui.w2_3.setText(str(self.arr_s[1]))
            self.ui.w3_3.setText(str(self.arr_s[2]))
            self.ui.w4_3.setText(str(self.arr_s[3]))
            self.ui.w5_3.setText(str(self.arr_s[4]))

            self.ui.label_10.setText(str(self.POC) + '$')
        except IndexError as e:
            logger.exception(f"{e}", exc_info=True)
        except SystemError as e:
            logger.error(f"{e}", exc_info=True)
        except Exception as e:
            print(f'{e}')
            logger.error(f"{e}", exc_info=True)

        logger.info(f'counted POC: {self.POC}$')

        return self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
               self.zone_75, self.zone_50, self.zone_25, self.price, self.POC

    @pyqtSlot()
    def create(self):
        try:
            self.bot.create_orders(self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50,
                                   self._zone_25, self.zone_150, self.zone_100,
                                   self.zone_75, self.zone_50, self.zone_25, self.price, self.POC)
        except Exception as e:
            if self.bot is None:
                self.ui.textBrowser.append("No orders received, at the beginning press the Start button")
            else:
                self.ui.textBrowser.append(f"{e}")
        else:
            self.ui.textBrowser.append(f"The orders was created successfully!")
            self.update_scrollbar()

    @pyqtSlot()
    def create_2(self):
        try:
            default_margin = min(self.arr_l, default=0)
            if default_margin == 0:
                self.ui.textBrowser.append(
                    'Not enough contracts size to create order! Please increase your deposit size or leverage')
                print('Not enough contracts size to create order! Please increase your deposit size or leverage')
                logger.info(f'Not enough contracts size to create order! Please increase your deposit size or leverage')
                return 0
            return self.bot.create_2_orders(default_margin, self._zone_150, self._zone_100, self._zone_75, self._zone_50,
                                             self._zone_25, self.zone_150, self.zone_100,
                                             self.zone_75, self.zone_50, self.zone_25, self.price, self.POC)

        except Exception as e:
            print(repr(e), e)
            logger.exception(e, exc_info=True)

    @pyqtSlot()
    def create_6(self):
        try:
            default_margin = min(self.arr_l, default=0)
            if default_margin == 0:
                self.ui.textBrowser.append(
                    'Not enough contracts size to create order! Please increase your deposit size or leverage')
                print('Not enough contracts size to create order! Please increase your deposit size or leverage')
                logger.info(f'Not enough contracts size to create order! Please increase your deposit size or leverage')
                return None, None, -1
            return self.bot.create_6_orders(default_margin, self._zone_150, self._zone_100, self._zone_75, self._zone_50,
                                             self._zone_25, self.zone_150, self.zone_100,
                                             self.zone_75, self.zone_50, self.zone_25, self.price, self.POC)

        except Exception as e:
            print(repr(e), e)
            logger.exception(e, exc_info=True)

    @pyqtSlot()
    def cancel(self):
        res = self.bot.cancel_orders()
        if not self.ui.checkAuto.isChecked():
            self.update_scrollbar()
        return res

    def cancel_orders_list(self, side_, buy_list, sell_list):
        print(self.is_orders)
        if side_ == 'Buy' and self.is_orders:
            print('BUY CANCEL')
            logger.info('BUY CANCEL')
            for order_id in sell_list:
                if not isinstance(order_id, bool):
                    res = self.session.cancel_active_order(
                        symbol="BTCUSD",
                        order_id=order_id
                    )
                    logger.info(f"{res}")
            self.is_orders = False
        elif side_ == 'Sell' and self.is_orders:
            print('SELL CANCEL')
            logger.info('SELL CANCEL')
            for order_id in buy_list:
                if not isinstance(order_id, bool):
                    res = self.session.cancel_active_order(
                        symbol="BTCUSD",
                        order_id=order_id
                    )
                    logger.info(f"{res}")
            self.is_orders = False


if __name__ == "__main__":

    try:
        app = QApplication([])
        application = MainWindow()
        application.show()

        sys.exit(app.exec())

    except SystemExit as e:
        print(f"SystemExit with code: {e}")
        while True:
            try:
                input('\nPress ENTER to exit')
                if keyboard.is_pressed('enter'):
                    logger.info(f"SystemExit with code: {e}")
                    break
            except:
                break
    except SystemError as e:
        print(f"SystemError with code: {e}")
        while True:
            try:
                input('\nPress ENTER to exit')
                if keyboard.is_pressed('enter'):
                    logger.info(f"SystemError with code: {e}")
                    break
            except:
                break
    except Exception as e:
        print(f"Exception with code: {e}")
        while True:
            try:
                input('\nPress ENTER to exit')
                if keyboard.is_pressed('enter'):
                    logger.info(f"Exception with code: {e}")
                    break
            except:
                break

