import os
import time
import pickle
import pandas as pd
import datetime as dt
from datetime import timedelta
from decision_map import Main, get_prediction_freq

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
    largest_freq = '30min'
    window = 30
    largest_freq = '30min'
    data_freq = ['1min', '5min', '15min', '30min']
    n_steps_ahead = 2
    
    df_by_freq, list_dates = get_prediction_freq(df, sample_by=largest_freq)
    print('Length of unique dates by largest frequency:', len(list_dates))
    print('Number of predictions should be :', len(list_dates)-window)
