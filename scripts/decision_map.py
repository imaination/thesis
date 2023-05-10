# Last Used/Updated: 5/10/2023

import os
import time
import pickle
import pandas as pd
import datetime as dt
from datetime import timedelta

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


def get_decision_map(df, horizon, window, data_freq, n_steps_ahead, list_dates):
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
        price_map = {key: [] for key in ['DateTime', 'High', 'Low', 'Open', 'Close']}
        
        for dfreq in data_freq:
            group_dt = data_slice.groupby(pd.Grouper(key='DateTime', freq=dfreq, label='right', closed='right')).mean().reset_index()
            group_dt = group_dt.dropna()
            price_map['DateTime'].append(group_dt['DateTime'].tail(window))
            price_map['High'].append(group_dt['High'].tail(window))
            price_map['Low'].append(group_dt['Low'].tail(window))
            price_map['Open'].append(group_dt['Open'].tail(window))
            price_map['Close'].append(group_dt['Close'].tail(window))
        # Ex: grab the nearest 15min prediction horizon (nearest because sometimes that min tick data does not exist)
        try:
            future = df[df['DateTime'].astype(str) >= list_dates[index + n_steps_ahead]].iloc[0]
        except IndexError as e:
            print(f"{e}")
            break
        current = data_slice.iloc[-1]
        delta = future["DateTime"] - current["DateTime"]
        
        if horizon == 'SCALP':
            # SCALP
            # this is the case when friday -> sunday; saturday is a non-trading day so skip
            if delta.days >= 2:
                print("current :", current["DateTime"])
                print("future :", future["DateTime"])
                print("Days between :", delta.days)
                print("Skip this index: ", index)
                index += 1
                continue
        elif horizon == 'SWING':
            # SWING
            if delta.days >= 5:
                print("current :", current["DateTime"])
                print("future :", future["DateTime"])
                print("Days between :", delta.days)
                print("Skip this index: ", index)
                index += 1
                continue
            
        decision = trading_action(future_close=future['Close'], current_close=current["Close"])
        
        print("current: ", current["DateTime"])
        print("future: ", future["DateTime"])
        decision_map[decision].append([list_dates[index+n_steps_ahead], price_map])
        index += 1

    return decision_map
    
    
def Main(arg):
    """
    :return: None
    """
    time = Time()
    time.print_start()
    df, horizon, window, data_freq, n_steps_ahead, list_dates = arg
    dm = get_decision_map(df, horizon, window, data_freq, n_steps_ahead, list_dates)
    time.print_end()
    return dm

