import pandas as pd
from users.models import CustomUser,Order, OrderItems, StoreItem
import json
from .rec import * #TODO: fix this with correct path?

#################################
# Item recommendation API logic #
#################################
def recommendItemsInStore(user_id, store_id, k):
  user_to_purchase_counts={}
  for user in CustomUser.objects.filter():
    store_item_orders={}
    orders=Order.objects.filter(user=user)
    for order in orders:
      store=order.store
      order_store_id=store.store_id
      if order_store_id==store_id:
        products=OrderItems.objects.filter(order=order)
        for product in products:
          product_id=product.item.item_id
          if product_id not in store_item_orders:
            store_item_orders[product_id]=0
          store_item_orders[product_id]+=1
    user_to_purchase_counts[user.id]=store_item_orders
  data_list=[]
  for user in user_to_purchase_counts.keys():
    for item in user_to_purchase_counts[user].keys():
      row=[]
      row.append(user)
      row.append(item)
      row.append(user_to_purchase_counts[user][item])
      data_list.append(row)
  data=pd.DataFrame(data_list, columns = ['user_id', 'item_id', 'purchase_count'])
  user_column='user_id'
  item_column='item_id'
  freq_column='purchase_count'
  recommendations= get_best_k_items(data, user_column=user_column, item_column=item_column, freq_column=freq_column, k=k, user_id=user_id)
  rec_dict={};
  rec_dict["recommendations"]=recommendations
  response_recommendations=rec_dict
  return response_recommendations



##################################
# Store recommendation API logic #
# ##################################
def recommendStore(user_id, k):
  merchant_user_to_purchase_counts={}
  for user in CustomUser.objects.filter():
    store_visits={}
    orders=Order.objects.filter(user=user)
    for order in orders:
      store=order.store
      store_id=store.store_id
      if store_id not in store_visits:
        store_visits[store_id]=0
      store_visits[store_id]+=1
    merchant_user_to_purchase_counts[user.id]=store_visits
  merchant_data_list=[]
  for user in merchant_user_to_purchase_counts.keys():
    for store in merchant_user_to_purchase_counts[user].keys():
      row=[]
      row.append(user)
      row.append(store)
      row.append(merchant_user_to_purchase_counts[user][store])
      merchant_data_list.append(row)
  merchant_data= pd.DataFrame(merchant_data_list, columns = ['user_id', 'merchant_id', 'purchase_count'])
  user_column='user_id'
  item_column='merchant_id'
  freq_column='purchase_count'
  merchant_recommendations= get_best_k_items(merchant_data, user_column=user_column, item_column=item_column, freq_column=freq_column, k=k, user_id=user_id)
  merchant_rec_dict={};
  merchant_rec_dict["recommendations"]=merchant_recommendations
  response_merchant_recommendations=json.dumps(merchant_rec_dict)
  return response_merchant_recommendations
