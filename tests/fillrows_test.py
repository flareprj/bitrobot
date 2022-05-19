from unittest import TestCase


def fills(deposit, qty_l, qty_s, orders_weights):
    res1 = []
    res2 = []

    while deposit > 0:
        for index, w in enumerate(orders_weights):
            if orders_weights[index] == 0:
                res1.insert(index, 0)
                res2.insert(index, 0)
                if index == 4:
                    deposit = 0
                    break
            else:
                item = int(deposit * orders_weights[index])
                res1.insert(index, item)
                res2.insert(index, item)
                deposit -= item

    matrix_l = [0, 0, 0, 0, 0]
    matrix_s = [0, 0, 0, 0, 0]

    for i in range(4, -1, -1):
        if qty_l > 0:
            matrix_l[i] = 1
            qty_l -= 1
        else:
            matrix_l[i] = 0
            qty_l -= 1

        if qty_s > 0:
            matrix_s[i] = 1
            qty_s -= 1
        else:
            matrix_s[i] = 0
            qty_s -= 1

    for index, val in enumerate(matrix_l):
        if matrix_l[index] == 0:
            res1[index] = 0
    for index, val in enumerate(matrix_s):
        if matrix_s[index] == 0:
            res2[index] = 0

    return res1, res2


class FillRows(TestCase):
    def setUp(self) -> None:
        self.deposit = 100

    def test_1(self):
        orders_weights = [0.1, 0.19, 0.3, 0.45, 1]
        x, y = fills(self.deposit, 4, 2, orders_weights)
        print(orders_weights)
        print(self._testMethodName, x, y)
        print('****************************')

    def test_2(self):
        orders_weights = [0.1, 0, 0, 0, 0]
        x, y = fills(self.deposit, 3, 5, orders_weights)
        print(orders_weights)
        print(self._testMethodName, x, y)
        print('****************************')

    def test_3(self):
        orders_weights = [0, 0, 0.3, 0.5, 1]
        x, y = fills(self.deposit, 1, 2, orders_weights)
        print(orders_weights)
        print(self._testMethodName, x, y)
        print('****************************')

    def test_4(self):
        orders_weights = [0, 0.1, 0.3, 0, 1]
        x, y = fills(self.deposit, 4, 2, orders_weights)
        print(orders_weights)
        print(self._testMethodName, x, y)
        print('****************************')

    def test_5(self):
        orders_weights = [0, 0.1, 0.3, 0, 1]
        x, y = fills(self.deposit, 3, 3, orders_weights)
        print(orders_weights)
        print(self._testMethodName, x, y)
        print('****************************')
