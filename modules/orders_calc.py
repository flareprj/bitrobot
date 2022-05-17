import pprint


def count_deposit(price, available_balance, leverage, percent):
    fees = 1 - (0.00075 * 2)
    return int(price * available_balance * leverage * percent * fees)


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


# 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711


if __name__ == "__main__":
    n = 66
    init = [0, 1]

    [init.append(sum(init[-2:])) for _ in range(n)]

    print(init[-1])

