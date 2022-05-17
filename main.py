import pprint
import time
import sys
import random
from pybit.inverse_perpetual import HTTP
from modules.strategy import *
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtCore import pyqtSlot, QThreadPool, QTimer, QThread, QRunnable, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QTextEdit,
    QDialog
)
from gui.qt6 import Ui_MainWindow
from gui.about import Ui_Dialog


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
        self.order_weights = None
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

        self.ui.api_key.setText('kENyGGsOnjJuLvIYqQ')
        self.ui.api_secret.setText('jxaVvRLTUqE5ds8CejCTwkYoEUJ9niuovJ1l')
        self.ui.lineEdit_3.setText('1')
        self.ui.lineEdit_4.setText('200')
        self.ui.lineEdit_5.setText('5')
        self.ui.lineEdit_6.setText('0.5')

        self.ui.w1.setText('0.1')
        self.ui.w2.setText('0.19')
        self.ui.w3.setText('0.3')
        self.ui.w4.setText('0.45')
        self.ui.w5.setText('1')

        self.ui.checkAuto.setChecked(True)

        self.thread_manager = QThreadPool()

        self.ui.startButton.clicked.connect(self.get_data_init)
        self.ui.stopButton.clicked.connect(self.stop_process)
        self.ui.createButton.clicked.connect(self.create)
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.resetButton.clicked.connect(self.reset)

        self.ui.actionExit.triggered.connect(lambda: QApplication.quit())
        self.ui.actionAbout.triggered.connect(self.about)

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
        self.ui.w1.setText('0.1')
        self.ui.w2.setText('0.19')
        self.ui.w3.setText('0.3')
        self.ui.w4.setText('0.45')
        self.ui.w5.setText('1')

    @pyqtSlot()
    def get_data_init(self):
        self.api_key = self.ui.api_key.text()
        self.api_secret = self.ui.api_secret.text()

        if self.api_key == '' or self.api_secret == '':
            self.ui.textBrowser.append(f"Api keys is empty")
            return

        allow_limit = [str(i) for i in range(5, 201, 1)]

        if self.ui.test_rb.isChecked():
            self.radio = True
        else:
            self.radio = False

        list_tf_main = ['1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M']
        list_tf_test = ['D', 'W', 'M']

        check_tf = self.ui.lineEdit_3.text()
        check_limit = self.ui.lineEdit_4.text()

        # TEST OR MAIN?
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

        if check_limit not in allow_limit:
            self.ui.textBrowser.append(f"The number of candles must be at least 5")
            return

        try:
            int(self.ui.lineEdit_5.text())
            int(self.ui.lineEdit_4.text())
            round(float(self.ui.lineEdit_6.text()), 2)
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

        self.ui.textBrowser.append('connecting..')
        self.bot = Strategy(self.radio, "BTCUSD", self.api_key, self.api_secret, MainWindow)

        if self.radio:
            self.session = HTTP("https://api-testnet.bybit.com", api_key=self.api_key,
                                api_secret=self.api_secret,
                                recv_window=10000)
        else:
            self.session = HTTP("https://api.bybit.com", api_key=self.api_key,
                                api_secret=self.api_secret,
                                recv_window=10000)

        self.ui.textBrowser.append(f"get available balance..")
        self.balance = self.bot.data.available_balance()
        self.leverage = int(self.ui.lineEdit_5.text())

        # если вместо баланса получили код ошибки - выводим его в лог, далее программа останавливается
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
        else:
            if self.balance == 0:
                self.ui.textBrowser.append('Add money to your balance!')
                return
            else:
                self.ui.textBrowser.append(self.balance)
                return

        # self.thread_manager.start(self.thread_calc)
        _, _, x, y = self.qty_calc()
        while x != 5 or y != 5:
            _, _, x, y = self.qty_calc()
            print(f'\rLess levels then needs, wait.. x:{x}, y:{y}', end='')
            sleep(1)

        print('Levels are good, get the view')
        self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
        self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw()

        self.is_alive = True
        if self.is_alive:
            self.thread_manager.start(self.get_data)

    @pyqtSlot()
    def get_data(self):
        if self.ui.checkAuto.isChecked():
            self.ui.createButton.setEnabled(False)
            self.ui.cancelButton.setEnabled(False)
            self.cancel()
            self.create()

        while self.is_alive:
            if self.ui.checkAuto.isChecked():
                status = self.bot.show_order_status()
                order_id = ""
                print(status)
                if status == "New":
                    # ожидаем установки ордеров..
                    while status == "New":
                        status = self.bot.show_order_status()
                        self.update_scrollbar()
                        live_price = self.bot.get_live_price() + '$'
                        live_pnl = '0 BTC'
                        self.ui.label_12.setText(live_price)
                        self.ui.label_15.setText(live_pnl)

                        # через 10мин перестроить уровни
                        elapsed_time = 60 * 15
                        while elapsed_time > 0:
                            try:
                                status = self.bot.show_order_status()
                                if status == "Untriggered":
                                    break
                                print(f"\relapsed_time: {elapsed_time}sec", end='')
                                elapsed_time -= 1
                                sleep(1)
                            except Exception as e:
                                print('\n', e)

                        else:
                            print('\ntimer finished!')
                            self.cancel()
                            print('update levels..')
                            # перестраиваем уровни
                            _, _, x, y = self.qty_calc()
                            while x != 5 or y != 5:
                                _, _, x, y = self.qty_calc()
                                print(f'\rLess levels then needs, wait.. x:{x}, y:{y}', end='')
                                sleep(1)
                            self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
                            self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw()
                            print('redraw completed..')
                            sleep(1)
                            self.create()


                elif status == "Untriggered":
                    print("We have Untriggered order! Cancel another orders!")
                    self.cancel()
                    status = self.bot.show_order_status()
                    try:
                        order_id = \
                            self.bot.client.Order.Order_getOrders(symbol="BTCUSD",
                                                                  order_status="Untriggered").result()[
                                0]['result']['data'][0]['order_id']
                    except Exception as e:
                        print(e)
                    else:
                        print(f"untriggered_order_id:{order_id}")
                        while status == "Untriggered":
                            status = self.bot.show_order_status()
                            price = self.bot.get_live_price()
                            live_price = price + '$'
                            live_pnl = str(self.bot.get_live_pnl()) + ' BTC'
                            self.ui.label_12.setText(live_price)
                            self.ui.label_15.setText(live_pnl)
                            sleep(1)

                            try:
                                take_profit = float(
                                    self.bot.client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0][
                                        'result']['take_profit'])
                                last_price = float(self.bot.get_live_price())
                                entry_price = float(self.session.my_position(symbol="BTCUSD")['result']['entry_price'])

                                print(f"take_profit: {take_profit}")
                                print(f"last_price: {last_price}")
                                print(f"entry_price: {entry_price}")

                            except Exception as e:
                                print(repr(e), e)
                            else:
                                while take_profit == 0 and take_profit is not None:
                                    status = self.bot.show_order_status()
                                    take_profit = float(
                                        self.bot.client.Positions.Positions_myPosition(symbol="BTCUSD").result()[0][
                                            'result'][
                                            'take_profit'])
                                    if status != "Untriggered":
                                        entry_price = float(
                                            self.session.my_position(symbol="BTCUSD")['result']['entry_price'])
                                        break
                                    sleep(1)

                                if take_profit > entry_price != 0 and take_profit != 0:
                                    trigger_trailing = int(entry_price + ((take_profit - entry_price) / 2))
                                    print(f"trigger_trailing: {trigger_trailing}$")
                                elif take_profit < entry_price != 0 and take_profit != 0:
                                    trigger_trailing = int(entry_price - abs((take_profit - entry_price) / 2))
                                    print(f"trigger_trailing: {trigger_trailing}$")
                                else:
                                    print(f"trigger_trailing: ****")
                                    break

                                while True:
                                    active_pos = self.session.my_position(symbol="BTCUSD")['result']['size']
                                    if active_pos != 0 and active_pos is not None:
                                        try:
                                            sleep(1)
                                            res = self.session.set_trading_stop(symbol="BTCUSD", take_profit=0,
                                                                                trailing_stop=50,
                                                                                new_trailing_active=trigger_trailing)
                                            pprint.pprint(res)
                                        except Exception as e:
                                            print(e)
                                        else:
                                            if float(self.session.my_position(symbol="BTCUSD")['result'][
                                                         'trailing_stop']) != '0':
                                                print(
                                                    f"placing a trailing-stop: {trigger_trailing}$ - ok! time:{datetime.now()}")
                                                break

                        # ордер выполнен
                        print('Stop\Take Order was executed!')
                        status = self.bot.show_order_status()
                        print(status)
                        # отменяем текущий активный ордер по его id
                        try:
                            self.bot.client.Order.Order_cancel(symbol="BTCUSD", order_id=order_id).result()
                        except Exception as e:
                            print(e)
                        else:
                            self.cancel()
                            print('update levels..')
                            # перестраиваем уровни
                            _, _, x, y = self.qty_calc()
                            while x != 5 or y != 5:
                                _, _, x, y = self.qty_calc()
                                print(f'\rLess levels then needs, wait.. x:{x}, y:{y}', end='')
                                sleep(1)

                            self.arr_l, self.arr_s, self._zone_150, self._zone_100, self._zone_75, self._zone_50, self._zone_25, self.zone_150, self.zone_100, \
                            self.zone_75, self.zone_50, self.zone_25, self.price, self.POC = self.draw()
                            print('redraw completed..')
                            sleep(1)
                            self.create()

                else:
                    self.update_scrollbar()
                    live_price = self.bot.get_live_price() + '$'
                    live_pnl = str(self.bot.get_live_pnl()) + ' BTC'
                    self.ui.label_12.setText(live_price)
                    self.ui.label_15.setText(live_pnl)
                    sleep(1)
            else:
                self.ui.createButton.setEnabled(True)
                self.ui.cancelButton.setEnabled(True)
                self.update_scrollbar()
                live_price = self.bot.get_live_price() + '$'
                live_pnl = str(self.bot.get_live_pnl()) + ' BTC'
                self.ui.label_12.setText(live_price)
                self.ui.label_15.setText(live_pnl)
                sleep(1)

    @pyqtSlot()
    def stop_process(self):
        if self.is_alive:
            self.is_alive = False
            self.ui.textBrowser.append('Stop receiving the data')
            self.update_scrollbar()
        if not self.ui.startButton.isEnabled():
            self.ui.startButton.setEnabled(True)

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

        self.arr_l, self.arr_s, qty_l, qty_s = self.bot.count_orders(self.balance, self.leverage, self.interval,
                                                                     self.limit,
                                                                     self.percents, self.order_weights)

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
        except IndexError:
            pass

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

    @pyqtSlot()
    def cancel(self):
        res = self.bot.cancel_orders()
        self.ui.textBrowser.append(f"{res}")


if __name__ == "__main__":
    app = QApplication([])

    application = MainWindow()
    application.show()

    sys.exit(app.exec())
