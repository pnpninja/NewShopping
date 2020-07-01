import pandas as pd
import numpy as np
import turicreate as tc

# helper function for providing weighted results from recommenders
def interleave(similarity_recommended_items, popularity_recommended_items):
  result=[]
  ratio=int(len(similarity_recommended_items)/len(popularity_recommended_items))
  similarity_index=0
  popularity_index=0
  current=1
  
  while(similarity_index<len(similarity_recommended_items) and popularity_index<len(popularity_recommended_items)):
    if(current%ratio==0):
      result.append(popularity_recommended_items[popularity_index])
      popularity_index+=1
    else:
      result.append(similarity_recommended_items[similarity_index])
      similarity_index+=1
    current+=1
  
  while(similarity_index<len(similarity_recommended_items)):
    result.append(similarity_recommended_items[similarity_index])
    similarity_index+=1
  
  while(popularity_index<len(popularity_recommended_items)):
    result.append(popularity_recommended_items[popularity_index])
    popularity_index+=1
  
  return result
  
# helper function to check for potential coldstart issues
def check_coldstart(data, user_column, product_column, freq_column, k, user_id):
  if(len(data[product_column].unique())<k):
    return True
  if(len(data.loc[data[user_column]==user_id, product_column].unique())<int(k/3)):
    return True
  return False
  
def get_coldstart_recommendation(data, user_column, product_column, freq_column, k, user_id):
  # user-merchant interactions table
  interactions=pd.pivot_table(data, values=freq_column, index=user_column, columns=product_column)

  # normalize [0-1]
  interactions= (interactions-np.min(np.min(interactions)))/(np.max(np.max(interactions))-np.min(np.min(interactions)))

  # create dummy id, in order to columnize userId
  training_data=interactions.reset_index()
  training_data.index.names = [freq_column]
  training_data=pd.melt(training_data, id_vars=[user_column],value_name=freq_column).dropna()
  user_id=[user_id]
  
  k=min(k,len(data[product_column].unique()))
  
#  popularity_k= max(1,int(k/2)+1)
#  popularity_recommender= tc.recommender.popularity_recommender.create(tc.SFrame(training_data), user_id=user_column, item_id=product_column, target=freq_column, verbose=False)
#
#  popularity_recommendation=popularity_recommender.recommend(users=user_id, k=popularity_k, verbose=False)
#  popularity_recommended_items=[ a for a in popularity_recommendation[product_column]]
#
#  random_k= max(0,k-popularity_k)
#  remaining_items=[]
#  for product in data[product_column].unique():
#    if product not in popularity_recommended_items:
#      remaining_items.append(product)
#
#  np.random.shuffle(np.array(remaining_items))
#  random_recommended_items= remaining_items[0:random_k]
  
  remaining_items=[]
  for product in data[product_column].unique():
      remaining_items.append(product)
  
  np.random.shuffle(np.array(remaining_items))
  random_recommended_items= remaining_items[0:k]
  
#  return popularity_recommended_items+random_recommended_items
  return random_recommended_items



"""
Get best k product recommendations for a user.

Parameters
--------------------
    data             -- pandas dataframe, consisting of purchase count for every (purchased item, user) pair in a particular store
    user_column      -- string, name of the column in the dataframe corresponding to unique user_ids
    item_column      -- string, name of the column in the dataframe corresponding to unique product_ids
    freq_column      -- string, name of the column in the dataframe corresponding to purchase count
    k                -- int, number of recommendations
    user_id          -- string, user for whom recommendations are to be made

Returns
--------------------
    recommended_items  -- list of k item_ids as recommendations
"""
def get_best_k_items(data, user_column, item_column, freq_column, k, user_id):
  
  # deal with coldstarts
  if check_coldstart(data, user_column, item_column, freq_column, k, user_id):
    return get_coldstart_recommendation(data, user_column, item_column, freq_column, k, user_id)
  # user-item interactions table
  interactions=pd.pivot_table(data, values=freq_column, index=user_column, columns=item_column)
  
  # normalize [0-1]
  interactions= (interactions-np.min(np.min(interactions)))/(np.max(np.max(interactions))-np.min(np.min(interactions)))
  
  # create dummy id, in order to columnize userId
  training_data=interactions.reset_index()
  training_data.index.names = [freq_column]
  training_data=pd.melt(training_data, id_vars=[user_column],value_name=freq_column).dropna()
  user_id=[user_id]
  recommender= tc.recommender.item_similarity_recommender.create(tc.SFrame(training_data), user_id=user_column, item_id=item_column, target=freq_column, verbose=False)
  
  recommendation=recommender.recommend(users=user_id, k=k, verbose=False)
  
  recommended_items=[ a for a in recommendation[item_column]]
  
  return recommended_items
  

"""
Get best k merchant recommendations for a user.

Parameters
--------------------
   data             -- pandas dataframe, consisting of purchase/visit count for every (merchant, user) pair in a particular location
   user_column      -- string, name of the column in the dataframe corresponding to unique user_ids
   merchant_column      -- string, name of the column in the dataframe corresponding to unique merchant_ids
   freq_column      -- string, name of the column in the dataframe corresponding to purchase/visit count
   k                -- int, number of recommendations
   user_id          -- string, user for whom recommendations are to be made

Returns
--------------------
   recommended_items  -- list of k merchant_ids as recommendations
"""
def get_best_k_merchants(data, user_column, merchant_column, freq_column, k, user_id):

  # deal with coldstarts
  if check_coldstart(data, user_column, merchant_column, freq_column, k, user_id):
    return get_coldstart_recommendation(data, user_column, merchant_column, freq_column, k, user_id)
  
  # user-merchant interactions table
  interactions=pd.pivot_table(data, values=freq_column, index=user_column, columns=merchant_column)

  # normalize [0-1]
  interactions= (interactions-np.min(np.min(interactions)))/(np.max(np.max(interactions))-np.min(np.min(interactions)))

  # create dummy id, in order to columnize userId
  training_data=interactions.reset_index()
  training_data.index.names = [freq_column]
  training_data=pd.melt(training_data, id_vars=[user_column],value_name=freq_column).dropna()
  user_id=[user_id]
  
  popularity_weight=0.25 #heuristic
  popularity_k= max(1,int(popularity_weight*k))
  similarity_k= max(0,k-popularity_k);
  
  similarity_recommender= tc.recommender.item_similarity_recommender.create(tc.SFrame(training_data), user_id=user_column, item_id=merchant_column, target=freq_column, verbose=False)

  similarity_recommendation=similarity_recommender.recommend(users=user_id, k=similarity_k, verbose=False)
  
  popularity_recommender= tc.recommender.popularity_recommender.create(tc.SFrame(training_data), user_id=user_column, item_id=merchant_column, target=freq_column, verbose=False)
  
  popularity_recommendation=popularity_recommender.recommend(users=user_id, k=popularity_k, verbose=False)

  similarity_recommended_items=[ a for a in similarity_recommendation[merchant_column]]
  popularity_recommended_items=[ a for a in popularity_recommendation[merchant_column]]
  
  recommended_items=interleave(similarity_recommended_items, popularity_recommended_items)

  return recommended_items
  


def main():
  # sample usage
  data= pd.read_csv('music_data.csv', usecols=['userId','artistId','plays'], encoding= 'unicode_escape')
  artist_data= pd.read_csv('music_data.csv', usecols=['artistId','artist'], encoding= 'unicode_escape')
  
  user_column='userId'
  artist_column='artistId'
  plays_column='plays'
  user_id=data[user_column].unique()[0] # example user
  recommendations= get_best_k_items(data, user_column=user_column, item_column=artist_column, freq_column=plays_column, k=10, user_id=user_id)
  
  # map artist names
  artistId_to_artistName={}
  artists=artist_data.artistId.unique()
  for a in artists:
    artistId_to_artistName[a]=artist_data.loc[artist_data['artistId']==a, 'artist'].unique()[0]
    
  recommended_artists=[artistId_to_artistName[a] for a in recommendations]
  print(recommended_artists)
  

if __name__ == '__main__':
  main()
