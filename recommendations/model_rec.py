import pandas as pd
import numpy as np
import turicreate as tc

# read data
orig_data= pd.read_csv('music_data.csv', usecols=['userId','artistId','artist', 'plays'], encoding= 'unicode_escape')
data= pd.read_csv('music_data.csv', usecols=['userId','artistId','plays'], encoding= 'unicode_escape')

# user-item interactions table
interactions=pd.pivot_table(data, values='plays', index='userId', columns='artistId')

#print(np.count_nonzero(~np.isnan(interactions)))
#10000 artists listened to, 10000 users => ~1 artists/user
#print(np.max([np.count_nonzero(r) for r in ~np.isnan(interactions)]))
#returns 1

# normalize [0-1]
interactions= (interactions-np.min(np.min(interactions)))/(np.max(np.max(interactions))-np.min(np.min(interactions)))

# create dummy id, in order to columnize userId
training_data=interactions.reset_index()
training_data.index.names = ['plays']
training_data=pd.melt(training_data, id_vars=['userId'],value_name='plays').dropna()

rec= tc.recommender.item_similarity_recommender.create(tc.SFrame(training_data), user_id='userId', item_id='artistId', target='plays', verbose=False)

dummy_user=['00d56a125a04426daec7cf81d61d6bd7e7364a86']
dummy_rec=rec.recommend(users=dummy_user, k=10, verbose=False)

# map artist names
artistId_to_artistName={}
artists=orig_data.artistId.unique()
for a in artists:
  artistId_to_artistName[a]=orig_data.loc[orig_data['artistId']==a, 'artist'].unique()[0]

dummy_rec_artists=[artistId_to_artistName[a] for a in dummy_rec["artistId"]]
#print(dummy_rec)
#print("Recommended Artists")
print(dummy_rec_artists)





