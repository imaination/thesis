# Last Used/Updated: 4/7/2023

# PURPOSE:
# Generate Technical Indicator images using the data made in 02_group_label_data

#!pip install pandas_ta
#!pip install plotly
#!pip3 install -U kaleido
from matplotlib import pyplot as plt
import pandas as pd
import pandas_ta as ta
import os
import pickle
import datetime

# ORDER BY

# 1. ta.sma       (t)
# 2. ta.wma       (t)
# 3. ta.ema       (t)
# 4. ta.hma       (t)
# 5. ta.tema      (t)
# 6. ta.cci       (m) compares current prices and the average price over a period of time
# 7. ta.willr     (m) determines overssold/overbought like rsi
# 8. help(ta.rsi) (m) shows historical strength/weakness of prices
# 9. ta.cmo      (m) similar to rsi
# 10. ta.aroon    (m) attempts to identify if a security is trending and how strong
# 11. ta.macd     (m) shows trend
# 12. ta.ppo      (m) similar to macd
# 13. ta.dm       (m) shows trend's strength and direction
# 14. ta.psar      (m) determines points of potentioal stop and reverses
# 15. ta.roc      (m) speed of price change over a period of time


# RSI
# The Relative Strength Index is popular momentum oscillator used to measure the
# velocity as well as the magnitude of directional price movements.

# willr
# William's Percent R is a momentum oscillator similar to the RSI that
# attempts to identify overbought and oversold conditions.

#wma
# The Weighted Moving Average where the weights are linearly increasing and
#     the most recent data has the heaviest weight.
    
# Exponential Moving Average (EMA)
# The Exponential Moving Average is more responsive moving average compared to the
# Simple Moving Average (SMA).  The weights are determined by alpha which is
# proportional to it's length.  There are several different methods of calculating
# EMA.  One method uses just the standard definition of EMA and another uses the
# SMA to generate the initial value for the rest of the calculation.

# Simple Moving Average (SMA)
# The Simple Moving Average is the classic moving average that is the equally
# weighted average over n periods.

#Bollinger Bands (BBANDS)
# A popular volatility indicator by John Bollinger.
    
# Triple Exponential Moving Average (TEMA)
# A less laggy Exponential Moving Average.

# Commodity Channel Index (CCI)
# Commodity Channel Index is a momentum oscillator used to primarily identify
# overbought and oversold levels relative to a mean.


# Chande Momentum Oscillator (CMO)
# Attempts to capture the momentum of an asset with overbought at 50 and
# oversold at -50.


# Moving Average Convergence Divergence (MACD)
# The MACD is a popular indicator to that is used to identify a security's trend.
# While APO and MACD are the same calculation, MACD also returns two more series
# called Signal and Histogram. The Signal is an EMA of MACD and the Histogram is
# the difference of MACD and Signal.

# Percentage Price Oscillator (PPO)
# The Percentage Price Oscillator is similar to MACD in measuring momentum.


# Rate of Change (ROC)
# Rate of Change is an indicator is also referred to as Momentum (yeah, confusingly).
# It is a pure momentum oscillator that measures the percent change in price with the
# previous price 'n' (or length) periods ago.

# Aroon & Aroon Oscillator (AROON)
# Aroon attempts to identify if a security is trending and how strong.
    
# Directional Movement (DM)
# The Directional Movement was developed by J. Welles Wilder in 1978 attempts to
# determine which direction the price of an asset is moving. It compares prior
# highs and lows to yield to two series +DM and -DM.

def normalize_0_255(columns, delta=0.0001):
    frames = []
    for column in columns:
        col_max = 0
        # Normalize image to between 0 and 255
        if column.max() == 0:
            col_max += delta
        else:
            col_max = column.max()
        column *= (255.0/col_max)
        frames.append(column)
    return pd.concat(frames, axis=1, ignore_index=True)
    

def create_technical_indicator_data(idx, label, loaded_dict, LEN=7, window_size=30):
    image_name = loaded_dict[label][idx][0]
    image_name='{0}.png'.format(image_name.replace('-','_').replace(' ','_').replace(':','_'))
    print(image_name)
    
    high_price = loaded_dict[label][idx][1]['High'][3]
    close_price = loaded_dict[label][idx][1]['Close'][3]
    low_price = loaded_dict[label][idx][1]['Low'][3]

    high_price_0 = loaded_dict[label][idx][1]['High'][0]
    close_price_0 = loaded_dict[label][idx][1]['Close'][0]
    low_price_0 = loaded_dict[label][idx][1]['Low'][0]
        
    high_price_1 = loaded_dict[label][idx][1]['High'][1]
    close_price_1 = loaded_dict[label][idx][1]['Close'][1]
    low_price_1 = loaded_dict[label][idx][1]['Low'][1]
    
    high_price_2 = loaded_dict[label][idx][1]['High'][2]
    close_price_2 = loaded_dict[label][idx][1]['Close'][2]
    low_price_2 = loaded_dict[label][idx][1]['Low'][2]
    
    sma = ta.sma(close=close_price, length=LEN).reset_index(drop=True)
    wma = ta.wma(close=close_price, length=LEN).reset_index(drop=True)
    ema = ta.ema(close=close_price_0, length=LEN).reset_index(drop=True)
    hma = ta.hma(close=close_price_1, length=LEN).reset_index(drop=True)
    tema = ta.tema(close=close_price_2, length=LEN).reset_index(drop=True)
    cci = ta.cci(high=high_price, low=low_price, close=close_price, length=LEN).reset_index(drop=True)
    willr = ta.willr(high=high_price, low=low_price, close=close_price, length=LEN).reset_index(drop=True)
    rsi = ta.rsi(close=close_price, length=LEN).reset_index(drop=True)
    cmo = ta.cmo(close=close_price, length=LEN).reset_index(drop=True)
    aroon = ta.aroon(high=high_price, low=low_price, length=LEN).reset_index(drop=True)
    macd = ta.macd(close=close_price, fast=3, slow=7, signal=5).reset_index(drop=True)
    ppo = ta.ppo(close=close_price_0, fast=7, slow=12, signal=9).reset_index(drop=True)
    dm = ta.dm(high=high_price_1, low=low_price_1, length=LEN).reset_index(drop=True)
    psar = ta.psar(high=high_price, low=low_price, close=close_price).reset_index(drop=True)
    roc = ta.roc(close=close_price, length=LEN).reset_index(drop=True)
    
    macd, histogram_macd, signal_macd = macd.iloc[:,0], macd.iloc[:,1], macd.iloc[:,2]
    ppo, histogram_ppo, signal_ppo = ppo.iloc[:,0], ppo.iloc[:,1], ppo.iloc[:,2]
    aroon_up, aroon_down, aroon_osc = aroon.iloc[:,0], aroon.iloc[:,1], aroon.iloc[:,2]
    DMP, DMN = dm.iloc[:,0], dm.iloc[:,1]
    long_psar, short_psar, af_psar, reversal_psar = psar.iloc[:,0], psar.iloc[:,1], psar.iloc[:,2], psar.iloc[:,3]
    
    cols = [sma, wma, ema, hma, tema, cci, willr, rsi, cmo, aroon_osc, macd, ppo, DMP, DMN, roc, long_psar, short_psar, af_psar, reversal_psar]
    df = normalize_0_255(cols)
    df.columns = ['sma', 'wma', 'ema', 'hma', 'tema', 'cci', 'willr', 'rsi', 'cmo', 'aroon', 'macd', 'ppo', 'DMP', 'DMN', 'roc', 'long_psar', 'short_psar', 'af_psar', 'reversal_psar']
    df.reset_index(inplace=True, drop=True)
    # take out the first few missing NaN values since we need symmetrical image size
#     end = start + window_size
    df = df.iloc[-len(df.columns):,]
     
    #ffill Nan values
    df.fillna(method='backfill', inplace=True)
    df.fillna(method='ffill', inplace=True)
    
    return image_name, df.T
    

def create_techical_indicator_images(idx, label, horizon, path, loaded_dict):
    img_name, chart_df = create_technical_indicator_data(idx, label, loaded_dict)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.imshow(chart_df.to_numpy(), cmap='gray', vmin=0, vmax=255)
    ax.axis('off')
    destination = label
    out_path = os.path.join(path, 'TRAIN/{}/TI'.format(horizon))
    repo = os.path.join(out_path, destination)
    fig.savefig(os.path.join(repo, img_name), bbox_inches='tight')
    plt.close(fig)


def Main():
    # Get path to file
    PATH = os.path.dirname(os.getcwd())
    data_path = os.path.join(PATH, 'data')
    #SCALP
#     W30_H2_DF30_V01_03_26_2023.pkl
#     W30_H2_DF30_V23_03_26_2023.pkl
#     W30_H2_DF30_V45_03_26_2023.pkl
#     W30_H2_DF30_V67_03_26_2023.pkl
    #SWING
#     W30_H3_DF24_V00_SWING_04_07_2023.pkl
    #POSITION
#     W30_H4_DF1W_V00_POSITION_04_07_2023.pkl


    #Stationary Data
    #SCALP
    #SCALP_STATIONARY_01.pkl
    #SCALP_STATIONARY_23.pkl
    #SCALP_STATIONARY_45.pkl
    #SCALP_STATIONARY_67.pkl
    #SWING
    #SWING_STATIONARY.pkl
    #POSITION
    #POSITION_STATIONARY.pkl
    
    file_name = 'POSITION_STATIONARY.pkl'
    file_path = os.path.join(data_path, file_name)
    # Open and Read file
    with open(os.path.join(data_path, file_name), 'rb') as f:
        loaded_dict = pickle.load(f)

#    horizon = 'SCALP' #'SCALP' #'SWING' #'POSITION'
    horizon = 'POSITION_ST' #'SCALP_ST' #'SWING_ST' #'POSITION_ST'
    label = 'SHORT' #'LONG' #
    destination = label

    for idx in range(len(loaded_dict[label])):
        create_techical_indicator_images(idx, label, horizon, PATH, loaded_dict)


if __name__ == '__main__':
    print("START!")
    Main()
    print("DONE!")
