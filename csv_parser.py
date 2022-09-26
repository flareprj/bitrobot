import pandas as pd


def save_csv(filename):
    df_new = pd.read_csv(filename, index_col=0, parse_dates=True)

    GFG = pd.ExcelWriter('src/new.xlsx')
    df_new.to_excel(GFG, index=False)
    GFG.save()


if __name__ == '__main__':
    save_csv(filename='src/Bybit-Derivatives-ClosedPNL-20220910-20220918.csv')

