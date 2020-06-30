import pandas as pd
import numpy as np
import turicreate as tc

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
  # user-item interactions table
  interactions=pd.pivot_table(data, values=freq_column, index=user_column, columns=item_column)
  
  # normalize [0-1]
  interactions= (interactions-np.min(np.min(interactions)))/(np.max(np.max(interactions))-np.min(np.min(interactions)))
  
  # create dummy id, in order to columnize userId
  training_data=interactions.reset_index()
  training_data.index.names = [freq_column]
  training_data=pd.melt(training_data, id_vars=[user_column],value_name=freq_column).dropna()

  recommender= tc.recommender.item_similarity_recommender.create(tc.SFrame(training_data), user_id=user_column, item_id=item_column, target=freq_column, verbose=False)
  
  recommendation=recommender.recommend(users=user_id, k=k, verbose=False)
  
  recommended_items=[ a for a in recommendation[item_column]
  
  return recommended_items
  


def get_best_k_merchants(data, user_column, merchant_column, freq_column, k, user_id):
  # user-merchant interactions table
  interactions=pd.pivot_table(data, values=freq_column, index=user_column, columns=merchant_column)

  # normalize [0-1]
  interactions= (interactions-np.min(np.min(interactions)))/(np.max(np.max(interactions))-np.min(np.min(interactions)))

  # create dummy id, in order to columnize userId
  training_data=interactions.reset_index()
  training_data.index.names = [freq_column]
  training_data=pd.melt(training_data, id_vars=[user_column],value_name=freq_column).dropna()
  
  popularity_weight=0.25
  popularity_k= int(popularity_weight*k)
  similarity_k= k-popularity_k;
  

  similarity_recommender= tc.recommender.item_similarity_recommender.create(tc.SFrame(training_data), user_id=user_column, item_id=merchant_column, target=freq_column, verbose=False)

  similarity_recommendation=similarity_recommender.recommend(users=user_id, k=similarity_k, verbose=False)
  
  popularity_recommender= tc.recommender.popularity_recommender.create(tc.SFrame(training_data), user_id=user_column, item_id=merchant_column, target=freq_column, verbose=False)
  
  popularity_recommendation=popularity_recommender.recommend(users=user_id, k=popularity_k, verbose=False)

  similarity_recommended_items=[ a for a in similarity_recommendation[merchant_column]
  popularity_recommended_items=[ a for a in popularity_recommendation[merchant_column]
  
  recommended_items=interleave(similarity_recommended_items, popularity_recommended_items)

  return recommended_items
