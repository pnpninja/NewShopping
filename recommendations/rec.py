import pandas as pd
import numpy as np
import turicreate as tc

orig_data= pd.read_csv('music_data.csv', usecols=['userId','artistId','artist', 'plays'], encoding= 'unicode_escape')
data= pd.read_csv('music_data.csv', usecols=['userId','artistId','plays'], encoding= 'unicode_escape')



