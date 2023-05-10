# Last Used/Updated: 4/7/2023

import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
from pyts.image import GramianAngularField
import pandas as pd
import os
from typing import *
from pandas.tseries.holiday import USFederalHolidayCalendar as Calendar
from multiprocessing import Pool
import datetime as dt
import pickle

#non-interactive process writing to file
matplotlib.use('Agg')


#pass time-series and create GAF image
def create_gaf(ts):
  data = dict()
  # print('ts shape: ', ts.shape) # shape should be index (so 20)
  gadf = GramianAngularField(method='difference', image_size=ts.shape[0]) #default  sample_range (-1, 1)
  # Fit to data, then transform it (X_new : Transformed array.)
  data['gadf'] = gadf.fit_transform(pd.DataFrame(ts).T)[0]
  return data

#create GAF images and saves them into destination repository
#concatnates 4 images as 1
# def create_images(X_plots, image_name, destination, horizon, image_matrix: tuple =(2, 2)):
def create_images(X_plots, image_name, destination, horizon, image_matrix, gaf_type):#: tuple =(1, 1)):
  fig = plt.figure(figsize=[img*4 for img in image_matrix]) #img*4 = 8 by 8
  grid = ImageGrid(fig,
                   111,
                   axes_pad=0,
                   nrows_ncols=image_matrix,
                   share_all=True,
                   )
  images = X_plots
  for image, ax in zip(images, grid):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow(image, cmap='rainbow', origin='lower')
    
  repo = os.path.join('../TRAIN/{}/{}'.format(horizon, gaf_type), destination)
  fig.savefig(os.path.join(repo, image_name))
  plt.close(fig)


def generate_gaf(images_data, h, agg=False):
  # decision -> LONG or SHORT
  # data -> [['2001-01-22', [114.243306, 114.636125, ...]
  if agg == True:
    gaf = 'GAF_AGG'
    tups = (2,2)
  else:
    tups = (1,1)
    gaf = 'GAF'
    
  for decision, data in images_data.items():
    # image_data[0] -> '2001-01-22'
    # image_data[1] -> [114.243306, 114.636125, ...]
    # so gets all ts data for SHORT/LONG
    for image_data in data:
        # transform time series into polar coordinates
        # to_plot -> 20 arrays of 20 values
        to_plot = [create_gaf(x)['gadf'] for x in image_data[1]]
        # create GAF images from array of polar coordinates
        #X_plots=transformed array, image_name=last data from selected range, destination is the folder SHORT/LONG
        create_images(X_plots=to_plot,
                      image_name='{0}'.format(image_data[0].replace('-','_').replace(' ','_').replace(':','_')),
                      destination=decision,
                      horizon = h,
                      image_matrix=tups,
                      gaf_type = gaf
        )
                      

def clean_dict(dict_):
    """
    Keep only neccessary features (gaf only uses closing prices)
    """
    for i in range(len(dict_)):
        temp = dict_[i][1]
        temp.pop("DateTime")
        temp.pop("High")
        temp.pop("Low")
        temp.pop("Open")
    return dict_


def format_dict(dict_, new_dict, key_, agg=False):
    """
    Format dictionary as {"LONG":[], "SHORT":[]}
    For aggregated GAF, use the entire closing prices but for not aggregated, use the closing price of the largest frequency
    """
    # dict_[i][0] is the prediction dates
    # dict_[i][1] are the closing prices
    if agg == False:
        for i in range(len(dict_)):
            new_dict[key_].append([dict_[i][0], [dict_[i][1]['Close'][3]]])
    if agg == True:
        for i in range(len(dict_)):
            new_dict[key_].append([dict_[i][0], list(dict_[i][1].values())[0]])
    return new_dict
    
    
def Main():
#SCALP
#W30_H2_DF30_V01_03_26_2023.pkl
#W30_H2_DF30_V23_03_27_2023.pkl
#W30_H2_DF30_V45_03_27_2023.pkl
#W30_H2_DF30_V67_03_27_2023.pkl
#SWING
#W30_H3_DF24_V00_SWING_04_07_2023.pkl
#POSITION
#W30_H4_DF1W_V00_POSITION_04_07_2023.pkl

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

    with open('../data/SCALP_STATIONARY_67.pkl', 'rb') as f:
        loaded_dict = pickle.load(f)

    # is the gaf image created using the largest frequency?
    
    #delete unnecessary data (only closing price is used to create the gaf image)
    long = clean_dict(loaded_dict["LONG"])
    short = clean_dict(loaded_dict["SHORT"])

    #create a clean dictionary
    aggregated_gaf = True
    temp_ = {'LONG':[], 'SHORT':[]}
    temp_ = format_dict(long, temp_, 'LONG', agg = aggregated_gaf)
    decision_map = format_dict(short, temp_, 'SHORT', agg = aggregated_gaf)


    print('GENERATING IMAGES')
    # Generate the images from processed data_slice
    generate_gaf(decision_map, h='SCALP_ST', agg = aggregated_gaf)
    # Log stuff
#     dt_points = dates.shape[0]
    total_short = len(decision_map['SHORT'])
    total_long = len(decision_map['LONG'])
    images_created = total_short + total_long
    print("========PREPROCESS REPORT========:\nTotal Images Created: {0}"
          "\nTotal LONG positions: {1}\nTotal SHORT positions: {2}".format(images_created,
                                                                            total_long,
                                                                            total_short))

if __name__ == '__main__':
    Main()
