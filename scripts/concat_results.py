# Last Used/Updated: 5/10/2023
# Purpose to concatnate pkl files for scalping because had to make four different files

import os
import time
import pickle
import pandas as pd

PATH = os.path.dirname(os.getcwd())
data_path = os.path.join(PATH, 'data')

def load_dict(data_path, filename):
    # Open and Read file
    with open(os.path.join(data_path, filename), 'rb') as f:
        loaded_dict = pickle.load(f)
    return loaded_dict
    
    
def append_results(result_, divide_by):
    dm = {}
    longs = result_[0]["LONG"]
    shorts = result_[0]["SHORT"]
    for i in range(1, divide_by):
        longs += result_[i]["LONG"]
        shorts += result_[i]["SHORT"]
    dm["LONG"] = longs
    dm["SHORT"] = shorts
    return dm
    
if __name__ == '__main__':
    f1 = load_dict(data_path, 'W30_H2_DF30_01_03_24_2023.pkl')
    f2 = load_dict(data_path, 'W30_H2_DF30_23_03_24_2023.pkl')
    f3 = load_dict(data_path, 'W30_H2_DF30_45_03_24_2023.pkl')
    f4 = load_dict(data_path, 'W30_H2_DF30_67_03_24_2023.pkl')
    fs = [f1, f2, f3, f4]
    result = append_results(fs, 4)
    print("Check length LONG:", len(result["LONG"]))
    print("Check length SHORT:", len(result["SHORT"]))
    # should be:
    # Check length LONG: 69 * 2 = 138
    #Check length SHORT: 70 * 2 = 140
