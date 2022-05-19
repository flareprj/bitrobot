import pprint


def count_deposit(price, available_balance, leverage, percent):
    fees = 1 - (0.00075 * 2)
    return int(price * available_balance * leverage * percent * fees)


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


def calc_orders(deposit, qty_l, qty_s, orders_weights):
    # list_max = [0.1, 0.19, 0.3, 0.45, 1]
    list_max = orders_weights
    deposit_s = deposit

    arr_l = []
    arr_s = []

    result_l = []
    result_s = []

    for i in range(qty_l):
        if i == qty_l - 1:
            arr_l.append(round(list_max[len(list_max) - 1], 2))
            break
        arr_l.append(round((list_max[i]), 2))

    #print('qty_longs:', arr_l)
    i = 0
    sum = 0
    while deposit > 0 and i < qty_l:
        if i == qty_l - 1:
            item = int(deposit * arr_l[len(arr_l) - 1])
            result_l.append(item)
            #print(f"item{i}:                {item}")
            sum += item
            break
        else:
            item = int(deposit * arr_l[i])
            result_l.append(item)
            #print(f"item{i}:                {item}")
            deposit -= item
            i += 1
            sum += item

    # print('--------')
    # print(f"sum:{sum}")

    for i in range(qty_s):
        if i == qty_s - 1:
            arr_s.append(round(list_max[len(list_max) - 1], 2))
            break
        arr_s.append(round((list_max[i]), 2))

    #print('qty_shorts:', arr_s)
    i = 0
    sum = 0
    while deposit_s > 0 and i < qty_s:
        if i == qty_s - 1:
            item = int(deposit_s * arr_s[len(arr_s) - 1])
            result_s.append(item)
            #print(f"item{i}:                {item}")
            sum += item
            break
        else:
            item = int(deposit_s * arr_s[i])
            result_s.append(item)
            #print(f"item{i}:                {item}")
            deposit_s -= item
            i += 1
            sum += item

    #print('--------')

    for i in range(0, 5, 1):
        try:
            #print(result_l[i])
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
            # print(result_s[i])
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
    deposit = 100
    orders_weights = [0.1, 0.19, 0.3, 0.45, 1]
    print(calc_orders(deposit, 5, 5, orders_weights))

    orders_weights = [0.1, 0, 0, 0, 0]
    print(calc_orders(deposit, 5, 5, orders_weights))


