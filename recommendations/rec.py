import pandas as pd
import numpy as np
import turicreate as tc

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
