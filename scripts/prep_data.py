# Last Used/Updated: 5/10/2023

import datetime as dt
import pandas as pd
import os
import sys

#NOTE:
#to run this, 
#prep_data.py ../data/ USDJPY.txt Ticker Date Time Open High Low Close Volume

def get_data(path, filename, col_names):
  rows = []
  with open(os.path.join(DATA_PATH, filename)) as content:
    for line in content:
      currentline = line.strip().split(",")
      rows.append(currentline)

  return pd.DataFrame(rows, columns=col_names)
    

def clean_data(data):
  print('Removing first row: ', data[:1])
  df = data[1:]
  
  print('Remove columns: Ticker, Volume')
  df.drop(['Ticker','Volume'], axis=1, inplace=True)

  print('Cast columns as type numeric from str: Open, High, Low, Close')
  for col in ['Open', 'High', 'Low', 'Close']:
    print('casting ' + col)
    df[col] = pd.to_numeric(df[col])

  print('Create a DateTime column with datetime format')
  df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y%m%d %-H%M%S', infer_datetime_format=True)
  
  return df


if __name__ == '__main__':
  # set path and column names
  DATA_PATH = sys.argv[1:2][0]
  filename = sys.argv[2:3][0]
  columns = sys.argv[3:]

  print('path to data: ', DATA_PATH)
  print('col names: ', columns)

  print('STEP 1: PREPROCESSING DATA')
  print('Open file, reading data')

  df = get_data(DATA_PATH, filename, columns)
  print('Raw data: ', df.head())
  
  print('Start Cleaning Data')
  df = clean_data(df)
  print('Cleaned dataframe: ', df.head())

  print('Export data as processed_{}.csv'.format(filename[:-4]))
  df.to_csv(os.path.join(DATA_PATH, 'preprocessed_{}.csv'.format(filename[:-4])))


















