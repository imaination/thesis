# Last Used/Updated: 4/10/2023

import os
import time
import pickle
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
from multiprocessing import Pool
from dateutil.relativedelta import relativedelta


class Time:
    """Time stamp for code execution"""
    
    def get_current_time(self):
        now = dt.datetime.now()
        return(now)
    
    def get_start_time(self):
        # Start time
        start_time = self.get_current_time()
        return(start_time)
       
    def get_end_time(self):
        # End time
        end_time = self.get_current_time()
        elapsed_time = end_time - self.get_start_time()
        return(end_time, elapsed_time)
        
    def print_start(self):
        print('--------Start Script--------')
        print('--------Start Time: ' + self.get_start_time().strftime('%Y-%m-%d %H:%M:%S') + '-------\n')

    def print_end(self):
        print('Total ' + str(self.get_end_time()[1].seconds) + ' [sec]')
        print('-----End Time : ' + self.get_end_time()[0].strftime('%Y-%m-%d %H:%M:%S') + ' ---------')
        print('-----END SCRIPT------')
        
        
def get_prediction_freq(df, sample_by):
    """
    input dataframe and sample frequency
    output a dataframe and a unique list of datetime by sample frequency
    """
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    # get unique list of dates by sample frequency
    df = df.set_index('DateTime')
    # documentation for resample method
    # close interval on the right so there are no time leakage
    #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html#pandas.DataFrame.resample
    df = df.resample(sample_by, label='right', closed='right').mean().reset_index()
    df = df.dropna()
    freq = df['DateTime']
    freq = freq.drop_duplicates()
    list_freq = freq.apply(str).tolist()
    return df, list_freq
    
    
def trading_action(future_close, current_close):
    '''
    input future closing price and current closing price
    return decision (LONG or SHORT)
    '''
    if current_close < future_close:
        decision = 'LONG'
    else:
        decision = 'SHORT'
    return decision


def get_bool_dec(decision):
    if decision == 'LONG':
        return 0
    return 1

def get_decision_map(df, window, data_freq, n_steps_ahead, list_dates):
    """
    Given
    df: preprocessed data from 01_prep_data
    window: window size (from which datatime to which datatime?)
    prediction horizon: how far (min/hrs/days) do you want to predict? ex: want to predict 15min ahead = 15Min
    data frequency: a list of frequency you want to aggregate the data to make the image (max is what you put for prediction horizon)
        # so if prediction horizon = 15Min, data frequency can have 1Min, 5Min, etc.. up till 15Min
    
    Outputs a pkl file in TRAIN/... path
    """
    decision_map = {key: [] for key in ['LONG', 'SHORT']}
    
    # index: same as window size but it increments within the loop
    index = window

    while True:
        # break the loop when index is greater than future values (no more data with window size to predict further values)
        # -2 because future value (value we want to predict) is set to index+1
        if index > len(list_dates) - n_steps_ahead:
            break

        # get a slice of data with specified window size
        data_slice = df.loc[(df['DateTime'] > list_dates[index - window]) & (df['DateTime'] <= list_dates[index])]
        
        # Ex: grab the nearest 15min prediction horizon (nearest because sometimes that min tick data does not exist)
        try:
            future = df[df['DateTime'].astype(str) >= list_dates[index + n_steps_ahead]].iloc[0]
        except IndexError as e:
            print(f"{e}")
            break
        current = data_slice.iloc[-1]
        delta = future["DateTime"] - current["DateTime"]
        
##        # SCRAPE
##        # this is the case when friday -> sunday; saturday is a non-trading day so skip
#        if delta.days >= 2:
#            print("current :", current["DateTime"])
#            print("future :", future["DateTime"])
#            print("Days between :", delta.days)
#            print("Skip this index: ", index)
#            index += 1
#            continue
        
#        # SWING
#        if delta.days >= 5:
#            print("current :", current["DateTime"])
#            print("future :", future["DateTime"])
#            print("Days between :", delta.days)
#            print("Skip this index: ", index)
#            index += 1
#            continue
            
        decision = trading_action(future_close=future['Close'], current_close=current["Close"])
        # 'CurrentValue', 'FutureValue', 'TrueLabel', 'Profit'
        profit_map = {'PredictionDate': list_dates[index+n_steps_ahead],
                  'CurrentValue': current["Close"],
                  'FutureValue': future['Close'],
                  'TrueLabel': get_bool_dec(decision),
                  'Profit': round(abs(current["Close"] - future['Close']), 2)}
        
        print("current: ", current["DateTime"])
        print("future: ", future["DateTime"])
        decision_map[decision].append(profit_map)
        index += 1

    return decision_map
    
    
def Main(arg):
    """
    :return: None
    """
    time = Time()
    time.print_start()
    df, window, data_freq, n_steps_ahead, list_dates = arg
    dm = get_decision_map(df, window, data_freq, n_steps_ahead, list_dates)
    time.print_end()
    return dm


def get_ranges(df, divide_by, list_dates, window, n_steps_ahead, data_freq):
    d_ranges = []
    start = 0
    start_idx = 0
    slices = len(list_dates)//divide_by
    first_dt = dt.datetime.strptime(list_dates[0], '%Y-%m-%d %H:%M:%S')
    start_dt = first_dt
    if divide_by == 1:
        return tuple([(df.iloc[:], window, data_freq, n_steps_ahead, list_dates[:])])
        
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
        d_ranges.append((df.iloc[start_idx:end_idx], window, data_freq, n_steps_ahead, freq_lst))
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
        d_ranges.append((df.iloc[start_idx:], window, data_freq, n_steps_ahead, list_dates[start:]))
    return tuple(d_ranges)


if __name__ == '__main__':
    print('READ AND LOAD DATA...')
    BASE_PATH = os.path.dirname(os.getcwd())
    DATA_DIR = 'data/'
    FILE_NM = 'preprocessed_USDJPY.csv'
    DATA_PATH = os.path.join(BASE_PATH, DATA_DIR)
    data = os.path.join(DATA_PATH, FILE_NM)
    df = pd.read_csv(data, sep=",")[['DateTime', 'High', 'Low', 'Open', 'Close']]
    print("Rows in df :", len(df))
    
    # Define variables
    divide_conquer = 16
    
#    # SCALP
#    largest_freq = '30min'
#    window = 30
#    n_steps_ahead = 2
#    data_freq = ['1min', '5min', '15min', '30min'] # data frequency for scralping

##     SWING
#    largest_freq = '24H'
#    window = 30
#    n_steps_ahead = 3
#    data_freq = ['4H', '8H', '12H', '24H'] # data frequency for swing

    # POSITION
    largest_freq = '1W'
    window = 20
    n_steps_ahead = 4
    data_freq = ['12H', '24H', '72H', '1W'] # data frequency for position '1W-WED'
    
    df_by_freq, list_dates = get_prediction_freq(df, sample_by=largest_freq)
    print('length of df_by_freq: ', len(list_dates))
    
    print('Starting task...')
    d_ranges = get_ranges(df, divide_conquer, list_dates, window, n_steps_ahead, data_freq)

    # create the process pool
    with Pool(8) as pool:
        #perform tasks here
        results_0 = pool.map(Main, d_ranges[:])
#        results_0 = pool.map(Main, d_ranges[:2])
#        results_1 = pool.map(Main, d_ranges[2:4])
#        results_2 = pool.map(Main, d_ranges[4:6])
#        results_3 = pool.map(Main, d_ranges[6:8])
#        results_4 = pool.map(Main, d_ranges[8:10])
#        results_5 = pool.map(Main, d_ranges[10:12])
#        results_6 = pool.map(Main, d_ranges[12:14])
#        results_7 = pool.map(Main, d_ranges[14:16])

#    longs = results_0[0]["LONG"] + results_0[1]["LONG"] + results_1[0]["LONG"] + results_1[1]["LONG"]
#    longs = results_2[0]["LONG"] + results_2[1]["LONG"] + results_3[0]["LONG"] + results_3[1]["LONG"]
#    longs = results_4[0]["LONG"] + results_4[1]["LONG"] + results_5[0]["LONG"] + results_5[1]["LONG"]
#    longs = results_6[0]["LONG"] + results_6[1]["LONG"] + results_7[0]["LONG"] + results_7[1]["LONG"]

#    shorts = results_0[0]["SHORT"] + results_0[1]["SHORT"] + results_1[0]["SHORT"] + results_1[1]["SHORT"]
#    shorts = results_2[0]["SHORT"] + results_2[1]["SHORT"] + results_3[0]["SHORT"] + results_3[1]["SHORT"]
#    shorts = results_4[0]["SHORT"] + results_4[1]["SHORT"] + results_5[0]["SHORT"] + results_5[1]["SHORT"]
#    shorts = results_6[0]["SHORT"] + results_6[1]["SHORT"] + results_7[0]["SHORT"] + results_7[1]["SHORT"]

##    # test
    longs = results_0[0]["LONG"] + results_0[1]["LONG"] + results_0[2]["LONG"] + results_0[3]["LONG"] + results_0[4]["LONG"] + results_0[5]["LONG"] + results_0[6]["LONG"] + results_0[7]["LONG"] + results_0[8]["LONG"] + results_0[9]["LONG"] + results_0[10]["LONG"] + results_0[11]["LONG"] + results_0[12]["LONG"] + results_0[13]["LONG"] + results_0[14]["LONG"] + results_0[15]["LONG"]
##
    shorts = results_0[0]["SHORT"] + results_0[1]["SHORT"] + results_0[2]["SHORT"] + results_0[3]["SHORT"] + results_0[4]["SHORT"] + results_0[5]["SHORT"] + results_0[6]["SHORT"] + results_0[7]["SHORT"] + results_0[8]["SHORT"] + results_0[9]["SHORT"] + results_0[10]["SHORT"] + results_0[11]["SHORT"] + results_0[12]["SHORT"] + results_0[13]["SHORT"] + results_0[14]["SHORT"] + results_0[15]["SHORT"]
    
    dm = {}
    dm["LONG"] = longs
    dm["SHORT"] = shorts
    print("Check length LONG:", len(dm["LONG"]))
    print("Check length SHORT:", len(dm["SHORT"]))
    
    now = dt.datetime.now() # current date and time
    today = now.strftime("%m_%d_%Y")
    # W:window, H:horizon, DF: datafrequency
    OUT_FILE = 'W{}_H{}_DF{}_{}_PROFIT_MAP_sr.pkl'.format('30', '2', '30_V00_POSITION', today)
    with open(os.path.join(DATA_PATH, OUT_FILE), 'wb') as f:
        pickle.dump(dm, f)
    print('DONE!')
