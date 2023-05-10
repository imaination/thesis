# Last Used/Updated: 5/10/2023

import os
import time
import pickle
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
from multiprocessing import Pool
from dateutil.relativedelta import relativedelta
from decision_map import Main, get_prediction_freq


def get_ranges(df, divide_by, list_dates, window, n_steps_ahead, data_freq, horizon):
    d_ranges = []
    start = 0
    start_idx = 0
    slices = len(list_dates)//divide_by
    first_dt = dt.datetime.strptime(list_dates[0], '%Y-%m-%d %H:%M:%S')
    start_dt = first_dt
    if divide_by == 1:
        return tuple([(df.iloc[:], horizon, window, data_freq, n_steps_ahead, list_dates[:])])
        
    for i in range(1, divide_by):
        end = slices * i + n_steps_ahead

        try:
            freq_lst = list_dates[start:end]
            end_dt = list_dates[end+n_steps_ahead]
        except IndexError:
            freq_lst = list_dates[start:]
            end_dt = list_dates[-1]
            
#        print('start, prev_start', start, prev_start)
        end_idx = df[df.DateTime <= end_dt].index[-1]
        print('first day, start day', first_dt, start_dt)
        print('start idx, end idx', start_idx, end_idx)
        d_ranges.append((df.iloc[start_idx:end_idx], horizon, window, data_freq, n_steps_ahead, freq_lst))
        # get one year ago from the start date since influence of past disturbances if any should be decaying
        start_dt = dt.datetime.strptime(list_dates[start], '%Y-%m-%d %H:%M:%S') - relativedelta(years=1)
        start = end - n_steps_ahead - window
        start_idx =  df[df.DateTime >= start_dt].index[0]
        if start < 0:
            start = 0
        # we dont have historical data before the first date on the table
        if start_dt <= first_dt:
            start_idx = 0
        
    # i need THE very end as well
    if start < len(list_dates):
        d_ranges.append((df.iloc[start_idx:], horizon, window, data_freq, n_steps_ahead, list_dates[start:]))
    return tuple(d_ranges)
    
    
if __name__ == '__main__':
    print('READ AND LOAD DATA...')
    BASE_PATH = os.path.dirname(os.getcwd())
    DATA_DIR = 'data/'
    FILE_NM = 'preprocessed_USDJPY.csv'
    DATA_PATH = os.path.join(BASE_PATH, DATA_DIR)
    data = os.path.join(DATA_PATH, FILE_NM)
    df = pd.read_csv(data, sep=",")[['DateTime', 'High', 'Low', 'Open', 'Close']]
#    df = df[:50000]
    print("Rows in df :", len(df))
    
    horizon = 'POSITION'
#    horizon = 'SCALP'
#    horizon = 'SWING'
    
    if horizon == "SCALP":
        # SCALP
        largest_freq = '30min'
        window = 30
        n_steps_ahead = 2
        data_freq = ['1min', '5min', '15min', '30min'] # data frequency for scalping
    elif horizon == "SWING"'
        # SWING
        largest_freq = '24H'
        window = 30
        n_steps_ahead = 3
        data_freq = ['4H', '8H', '12H', '24H'] # data frequency for swing
    elif horizon == 'POSITION':
        # POSITION
        largest_freq = '1W'
        window = 20
        n_steps_ahead = 4
        data_freq = ['12H', '24H', '72H', '1W'] # data frequency for position '1W-WED'
    
    # Define variables
    divide_conquer = 16
    df_by_freq, list_dates = get_prediction_freq(df, sample_by=largest_freq)
    print('length of df_by_freq: ', len(list_dates))
    
    print('Starting task...')
    d_ranges = get_ranges(df, divide_conquer, list_dates, window, n_steps_ahead, data_freq, horizon)

    if horizon == 'POSITION':
        # create the process pool
        with Pool(8) as pool:
            #perform tasks here
            results_0 = pool.map(Main, d_ranges[:])
            
        longs = results_0[0]["LONG"] + results_0[1]["LONG"] + results_0[2]["LONG"] + results_0[3]["LONG"] + results_0[4]["LONG"] + results_0[5]["LONG"] + results_0[6]["LONG"] + results_0[7]["LONG"] + results_0[8]["LONG"] + results_0[9]["LONG"] + results_0[10]["LONG"] + results_0[11]["LONG"] + results_0[12]["LONG"] + results_0[13]["LONG"] + results_0[14]["LONG"] + results_0[15]["LONG"]
        
        shorts = results_0[0]["SHORT"] + results_0[1]["SHORT"] + results_0[2]["SHORT"] + results_0[3]["SHORT"] + results_0[4]["SHORT"] + results_0[5]["SHORT"] + results_0[6]["SHORT"] + results_0[7]["SHORT"] + results_0[8]["SHORT"] + results_0[9]["SHORT"] + results_0[10]["SHORT"] + results_0[11]["SHORT"] + results_0[12]["SHORT"] + results_0[13]["SHORT"] + results_0[14]["SHORT"] + results_0[15]["SHORT"]
    
    else:
        # create the process pool
        with Pool(8) as pool:
            #perform tasks here
            results_0 = pool.map(Main, d_ranges[:2])
            results_1 = pool.map(Main, d_ranges[2:4])
            results_2 = pool.map(Main, d_ranges[4:6])
            results_3 = pool.map(Main, d_ranges[6:8])
            results_4 = pool.map(Main, d_ranges[8:10])
            results_5 = pool.map(Main, d_ranges[10:12])
            results_6 = pool.map(Main, d_ranges[12:14])
            results_7 = pool.map(Main, d_ranges[14:16])

        longs = results_0[0]["LONG"] + results_0[1]["LONG"] + results_1[0]["LONG"] + results_1[1]["LONG"]
        longs = results_2[0]["LONG"] + results_2[1]["LONG"] + results_3[0]["LONG"] + results_3[1]["LONG"]
        longs = results_4[0]["LONG"] + results_4[1]["LONG"] + results_5[0]["LONG"] + results_5[1]["LONG"]
        longs = results_6[0]["LONG"] + results_6[1]["LONG"] + results_7[0]["LONG"] + results_7[1]["LONG"]

        shorts = results_0[0]["SHORT"] + results_0[1]["SHORT"] + results_1[0]["SHORT"] + results_1[1]["SHORT"]
        shorts = results_2[0]["SHORT"] + results_2[1]["SHORT"] + results_3[0]["SHORT"] + results_3[1]["SHORT"]
        shorts = results_4[0]["SHORT"] + results_4[1]["SHORT"] + results_5[0]["SHORT"] + results_5[1]["SHORT"]
        shorts = results_6[0]["SHORT"] + results_6[1]["SHORT"] + results_7[0]["SHORT"] + results_7[1]["SHORT"]

    dm = {}
    dm["LONG"] = longs
    dm["SHORT"] = shorts
    print("Check length LONG:", len(dm["LONG"]))
    print("Check length SHORT:", len(dm["SHORT"]))
    now = dt.datetime.now() # current date and time
    today = now.strftime("%m_%d_%Y")
    # W:window, H:horizon, DF: datafrequency
    OUT_FILE = 'W{}_H{}_DF{}_{}_{}_{}.pkl'.format(window, n_steps_ahead, largest_freq, 'V00', horizon, today)
    with open(os.path.join(DATA_PATH, OUT_FILE), 'wb') as f:
        pickle.dump(dm, f)
    print('DONE!')
