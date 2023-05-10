import os

# set up folders/sub-folders
print('Creating Directories: ')
# the absolute path of the directory where the program resides
PATH = os.path.dirname(__file__)


horizons = ['SCALP', 'SCALP_ST', 'SWING', 'SWING_ST', 'POSITION', 'POSITION_ST']
image_types = ['GAF', 'GAF_ST', 'GAF_AGG', 'GAF_AGG_ST', 'CS', 'CS_ST', 'TI', 'TI_ST']
label_classes = ['LONG', 'SHORT']

# make TRAIN directory where all training data will be stored
TRAIN = os.path.join(PATH, 'TRAIN')

# paths to training folders by horizon
SCALP = os.path.join(TRAIN, 'SCALP')
INTRA = os.path.join(TRAIN, 'INTRA')
SWING = os.path.join(TRAIN, 'SWING')
MONTH = os.path.join(TRAIN, 'MONTH')

for horizon in horizons:
    for image_type in image_types:
        for label_class in label_classes:
            dir_name = os.path.join(TRAIN, horizon, image_type, label_class)
            if not os.path.exists(dir_name):
                print(f"Created directory: {dir_name}")
                os.makedirs(dir_name)
            else:
                print(f"Directory already exists: {dir_name}")
            
print('Created directory : ', 'saved_models')
os.makedirs(os.path.join(PATH, 'saved_models'))
