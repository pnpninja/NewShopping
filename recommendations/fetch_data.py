import pandas as pd

user_to_purchase_counts={}
for user in CustomUser.objects.filter():
  store_item_orders={}
  orders=Order.objects.filter(user=user)
  for order in orders:
    products=OrderItems.objects.filter(order=order)
    for product in products:
      product_id=product.item.item_id
      if product_id not in store_item_orders:
        store_item_orders[product_id]=0
      store_item_orders[product_id]+=1
  user_to_purchase_counts[user.id]=store_item_orders
  
data_list=[]
for user in user_to_purchase_counts.keys():
  for item in user_to_purchase_count[user].keys():
    row=[]
    row.append(user)
    row.append(item)
    row.append(user_to_purchase_count[user][item])
    data_list.append(row)

data= pd.DataFrame(data_list, columns = ['user_id', 'item_id', 'purchase_count'])
  
