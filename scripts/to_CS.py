# Last Used/Updated: 4/25/2023
# PURPOSE:
# Generate Candle Stick images using the data made in 02_group_label_data

#!pip install pandas_ta
#!pip install plotly
#!pip3 install -U kaleido
import pandas as pd
import pandas_ta as ta
import os
import plotly.graph_objects as go
import pickle
import datetime
# help(ta.bbands)

def prepare_data_cs(idx, label, loaded_dict):
    image_name = loaded_dict[label][idx][0]
    image_name='{0}.png'.format(image_name.replace('-','_').replace(' ','_').replace(':','_'))
    print(image_name)
    
    dt_ = pd.DataFrame(loaded_dict[label][idx][1]['DateTime'][3]).reset_index(drop=True)
    high_ = pd.DataFrame(loaded_dict[label][idx][1]['High'][3]).reset_index(drop=True)
    close_ = pd.DataFrame(loaded_dict[label][idx][1]['Close'][3]).reset_index(drop=True)
    open_ = pd.DataFrame(loaded_dict[label][idx][1]['Open'][3]).reset_index(drop=True)
    low_ = pd.DataFrame(loaded_dict[label][idx][1]['Low'][3]).reset_index(drop=True)
    time = [dt_["DateTime"].iloc[i].time() for i in range(len(dt_))]

    frames = [dt_, high_, close_, open_, low_]
    chart_df = pd.concat(frames, axis=1, ignore_index=True)
    chart_df.columns = ['DateTime', 'High', 'Close', 'Open', 'Low']
    chart_df["time"] = time
    return image_name, chart_df
    
    
def candle_stick_chart(idx, label, horizon, path, loaded_dict):
    img_name, chart_df = prepare_data_cs(idx, label, loaded_dict)
    
    # Add technical indicators (EMA & BollingerBands)
    chart_df['5EMA'] = ta.ema(chart_df['Close'], 5)
    
    # Initialize Bollinger Bands Indicator
    indicator_bb = ta.bbands(chart_df['Close'])
    
    # Add Bollinger Bands features
    chart_df['bb_lower'] = indicator_bb.iloc[:,0]
    chart_df['bb_mid'] = indicator_bb.iloc[:,1]
    chart_df['bb_upper'] = indicator_bb.iloc[:,2]
    chart_df['bb_bandwidth'] = indicator_bb.iloc[:,3]
    chart_df['bb_percent'] = indicator_bb.iloc[:,4]
    
    fig = go.Figure(data=[go.Candlestick(x=chart_df.DateTime,
                open=chart_df.Open,
                high=chart_df.High,
                low=chart_df.Low,
                close=chart_df.Close)])

    ema_trace = go.Scatter(x=chart_df['DateTime'], y=chart_df['5EMA'], mode='lines', name='5EMA')
    bb_lower = go.Scatter(x=chart_df['DateTime'], y=chart_df['bb_lower'], mode='lines', line=dict(color="#ffe476"), name='bb_lower')
    bb_upper = go.Scatter(x=chart_df['DateTime'], y=chart_df['bb_upper'], mode='lines', line=dict(color="#ffe476"), name='bb_upper')
    fig.add_trace(ema_trace)
    fig.add_trace(bb_lower)
    fig.add_trace(bb_upper)
    fig.update_layout(xaxis_rangeslider_visible=False,
                      showlegend=False,
                      plot_bgcolor='white'
                     )
    #x axis
    fig.update_xaxes(visible=False)

    #y axis
    fig.update_yaxes(visible=False)
    destination = label
    out_path = os.path.join(path, 'TRAIN/{}/CS'.format(horizon))
    repo = os.path.join(out_path, destination)
    fig.write_image(os.path.join(repo, img_name))
#    fig.show()
    

def Main():
    # Get path to file
    PATH = os.path.dirname(os.getcwd())
    data_path = os.path.join(PATH, 'data')
    #SCALP
#     W30_H2_DF30_V01_03_26_2023.pkl
#     W30_H2_DF30_V23_03_27_2023.pkl
#     W30_H2_DF30_V45_03_27_2023.pkl
#     W30_H2_DF30_V67_03_27_2023.pkl
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
    
    file_name = 'SCALP_STATIONARY_67.pkl'
    file_path = os.path.join(data_path, file_name)
    # Open and Read file
    with open(os.path.join(data_path, file_name), 'rb') as f:
        loaded_dict = pickle.load(f)

#    horizon = 'POSITION' #'SCALP' #'SWING' #
    horizon =  'SCALP_ST' #'SCALP_ST' #'SWING_ST' #'POSITION_ST'
    label = 'SHORT' # 'LONG' #'SHORT' #
    destination = label

    for idx in range(len(loaded_dict[label])):
        candle_stick_chart(idx, label, horizon, PATH, loaded_dict)
        

if __name__ == '__main__':
    Main()
