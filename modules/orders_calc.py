import pprint
import logging.config
from modules.settings import *

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')


def count_deposit(price, available_balance, leverage, percent):
    fees = 1 - (0.00075 * 2)
    return int(price * available_balance * leverage * percent/100 * fees)


def fills(deposit, qty_l, qty_s, orders_weights):
    res1 = []
    res2 = []

    while deposit > 0:
        for index, w in enumerate(orders_weights):
            if orders_weights[index]/100 == 0:
                res1.insert(index, 0)
                res2.insert(index, 0)
                if index == 4:
                    deposit = 0
                    break
            else:
                item = int(deposit * orders_weights[index]/100)
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

    logger.info(f"filled order matrix: {res1}, {res2}")

    return res1, res2


def calc_orders(deposit, qty_l, qty_s, list_max):
    deposit_save = deposit

    arr_l = []
    arr_s = []

    result_l = []
    result_s = []

    for i in range(qty_l):
        arr_l.append(list_max[i])

    i = 0
    while deposit > 0 and i < qty_l:
        item = int(deposit * arr_l[i]/100)
        result_l.append(item)
        deposit -= item
        i += 1

    for i in range(qty_s):
        arr_s.append(list_max[i])

    i = 0
    while deposit_save > 0 and i < qty_s:
        item = int(deposit_save * arr_s[i]/100)
        result_s.append(item)
        deposit_save -= item
        i += 1

    # *****************************************************************
    ''''
    Block for move founded contracts to end list and insert '0' values
    before - [10, 0, 0] [10, 0, 0, 40, 50]
    after - [0, 0, 10] [0, 0, 10, 40, 50]
    '''

    for i in range(0, 5, 1):
        try:
            pass
        except IndexError:
            result_l.append(0)

    a = result_l
    b = [x for x in a if x != 0]

    for i in a:
        if i == 0:
            b.insert(i, 0)
    result_l = b

    for i in range(0, 5, 1):
        try:
            pass
        except IndexError:
            result_s.append(0)

    a = result_s
    b = [x for x in a if x != 0]

    for i in a:
        if i == 0:
            b.insert(i, 0)
    result_s = b

    return result_l, result_s


if __name__ == "__main__":
    deposit = 50
    orders_weights = [10, 19, 30, 45, 100]

    #orders_weights = [100, 0, 0, 0, 0]
    print(calc_orders(deposit, 5, 5, orders_weights))


