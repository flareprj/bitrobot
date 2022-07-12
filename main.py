import http.client
import sys

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
        self.order_weights = [0.1, 0, 0, 0, 0]
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
    def reset(self):
        if not self.ui.checkAuto.isChecked():
            self.ui.w1.setText('0.1')
            self.ui.w2.setText('0.19')
            self.ui.w3.setText('0.3')
            self.ui.w4.setText('0.45')
            self.ui.w5.setText('1')
        else:
            self.ui.w1.setText('0.1')
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
        print(f"Starting..TF:{self.ui.lineEdit_3.text()}, CS:{self.ui.lineEdit_4.text()}, LE:{self.ui.lineEdit_5.text()}, "
              f"AA:{self.ui.lineEdit_6.text()}, TS:{self.ui.trailing_stop.text()}, TR:{self.ui.timer.text()}, time:{datetime.now()}")
        logger.info(f"Starting..TF:{self.ui.lineEdit_3.text()}, CS:{self.ui.lineEdit_4.text()}, LE:{self.ui.lineEdit_5.text()}, "
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
            if self.ui.checkAuto.isChecked():
                self.ui.createButton.setEnabled(False)
                self.ui.cancelButton.setEnabled(False)

                self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
                self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw_2()

                self.arr_l.extend(self.arr_s)
                self.arr_l = [x for x in self.arr_l if x != 0]

                res = self.create_2()
                if res == 0:
                    return
                sleep_()
            else:
                self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
                self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw()

        while self.is_alive:
            if self.ui.checkAuto.isChecked():
                self.status = self.bot.show_order_status()
                print(f'current_status: {self.status}')
                logger.info(f'current_status: {self.status}')
                if self.status == "New":
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
                                #live_price = self.bot.get_live_price() + '$'
                                #live_pnl = '0 BTC'
                                #self.ui.label_12.setText(live_price)
                                #self.ui.label_15.setText(live_pnl)
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
                    sleep_()
                    self.cancel()
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
                                sleep_()
                                self.cancel()
                            print(f'current_status: {self.status}')
                            sleep_()
                    else:
                        print(f"untriggered_order_id:{order_id}")
                        logger.info(f"untriggered_order_id:{order_id}")
                        while self.status == "Untriggered":
                            try:
                                sleep_()
                                take_profit = float(
                                    self.bot.client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0][
                                        'result']['take_profit'])
                                #last_price = float(self.bot.get_live_price())
                                sleep_()
                                entry_price = float(self.session.my_position(symbol="BTCUSD")['result']['entry_price'])
                                sleep_()
                                side = self.session.my_position(symbol="BTCUSD")['result']['side']

                                print(f"take_profit: {take_profit}")
                                #print(f"last_price: {last_price}")
                                print(f"entry_price: {entry_price}")
                                print(f"side: {side}")
                                logger.info(
                                    f"take_profit:{take_profit}, entry_price:{entry_price}, side:{side}")
                            except http.client.RemoteDisconnected as e:
                                print(repr(e), e)
                                logger.error(f"RemoteDisconnected, {e}")
                                sleep_()
                                continue
                            except requests.exceptions.ConnectionError as e:
                                print(repr(e), e)
                                logger.exception(e, exc_info=True)
                                sleep_()
                                continue
                            except Exception as e:
                                print(repr(e), e)
                                logger.exception(e, exc_info=True)
                                sleep_()
                                continue
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

                                while True:
                                    active_pos = self.session.my_position(symbol="BTCUSD")['result']['size']
                                    if active_pos != 0 and active_pos is not None:
                                        try:
                                            self.session.set_trading_stop(symbol="BTCUSD", take_profit=0,
                                                                          trailing_stop=self.trailing_stop,
                                                                          new_trailing_active=trigger_trailing)
                                        except Exception as e:
                                            print(e)
                                            logger.exception(f"{e}", exc_info=True)
                                            sleep_()
                                            continue
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
                                        #price = self.bot.get_live_price()
                                        #live_price = price + '$'
                                        #live_pnl = str(self.bot.get_live_pnl()) + ' BTC'
                                        #self.ui.label_12.setText(live_price)
                                        #self.ui.label_15.setText(live_pnl)
                                        print(f"\r{self.status}", end='')
                                        #print(f"\r{live_pnl}, entry_price:{entry_price}$", end='')
                                        sleep_()
                                        if self.status != "Untriggered":
                                            logger.info(f"IF BLOCK, {self.status}")
                                            break
                                    except http.client.RemoteDisconnected as e:
                                        logger.error(f"RemoteDisconnected, {e}")
                                        sleep_()
                                        continue
                                    except Exception as e:
                                        print(e)
                                        logger.exception(e, exc_info=True)
                                        sleep_()
                                        continue

                        print(f'\nStop-Take Order was executed! time:{datetime.now()}')
                        logger.info(f'Stop-Take Order was executed!')
                        self.update_redraw()
                        self.status = self.bot.show_order_status()
                        while self.status != "New":
                            self.status = self.bot.show_order_status()
                            if self.status == "Filled":
                                print(f"FAST FILLED")
                                logger.info(f"FAST FILLED")
                                self.cancel()
                            print(f'current_status: {self.status}')
                            sleep(1)
                elif not self.is_alive:
                    break
            else:
                self.ui.createButton.setEnabled(True)
                self.ui.cancelButton.setEnabled(True)
                live_price = self.bot.get_live_price() + '$'
                live_pnl = str(self.bot.get_live_pnl()) + ' BTC'
                self.ui.label_12.setText(live_price)
                self.ui.label_15.setText(live_pnl)
                sleep(1)

    @pyqtSlot()
    def stop_process(self):
        if self.is_alive:
            self.status = self.bot.show_order_status()
            if self.status == "Untriggered" or self.status == "New":
                res = self.cancel()
                self.ui.textBrowser.append(f'{res}')
            self.is_alive = False
            self.ui.textBrowser.append(f"Stop receiving the data, time:{datetime.now()}")
            print(f"Stop receiving the data, time:{datetime.now()}")
            logger.info(f"Stop receiving the data")
            self.update_scrollbar()
        if not self.ui.startButton.isEnabled():
            self.ui.startButton.setEnabled(True)

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
        res = self.create_2()
        if res == 0:
            return
        self.status = self.bot.show_order_status()

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
    def cancel(self):
        res = self.bot.cancel_orders()
        if not self.ui.checkAuto.isChecked():
            self.ui.textBrowser.append(f"{res}")
            self.update_scrollbar()
        return res


if __name__ == "__main__":
    app = QApplication([])

    application = MainWindow()
    application.show()

    sys.exit(app.exec())
