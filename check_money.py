import numpy as np
import pandas as pd


def main():
    df = pd.read_csv('./result.csv')
    res_list = df["result"].values

    get_list = []
    cur_amount = 0
    cur_amount_list = []

    for i,v in enumerate(res_list):
        if(i==0):
            get_list.append(0)
        else:
            if res_list[i-1] != res_list[i]:
                get_list.append(-1000)
            else:
                get_list.append(1000)
        cur_amount += get_list[-1]
        cur_amount_list.append(cur_amount)

        print(cur_amount)

    df['get'] = get_list
    df['amount'] = cur_amount
    df.to_csv('./result.csv')

if __name__ == '__main__':
    main()
