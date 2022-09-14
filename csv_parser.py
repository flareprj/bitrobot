import pandas as pd
from time import sleep


def save_csv(filename):
    df_new = pd.read_csv(filename, index_col=0, parse_dates=True)

    GFG = pd.ExcelWriter('src/new.xlsx')
    df_new.to_excel(GFG, index=False)
    GFG.save()


def stop_process(check_levels=0):
    print(check_levels)
    if check_levels == 1:
        print(f'finding new levels..')
        list_tf = ['1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M']
        current_tf = '1'
        for i, tf in enumerate(list_tf, start=0):
            if tf == current_tf:
                new_tf = list_tf[i - 1]
                print(f'new_tf: {new_tf}')
                sleep(1)
                # break


if __name__ == '__main__':
    # save_csv(filename='src/BybitClosedPNLInversePerpetual20220801-20220818.csv')
    #stop_process(check_levels=1)

    i = 1
    while i > 3:
        print(i)
        i = 1
        if i == 1:
            break
    else:
        print('break', i)
