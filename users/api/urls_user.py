from django.urls import include,path
from .views_user import PersonalUserDetailView, StoreDetailView, StoreImageChangeView, StoreItemsView, CreateOrUpdateStoreItemsView, StoreItemImageChangeView, CartItemsView, CreateOrUpdateStoreItemsView2, OrderProcess, RecommendationView, StoreRecommendationView

urlpatterns = [
	path('users/userdetails', PersonalUserDetailView.as_view(), name='hello'),
	path('stores/<int:store_id>', StoreDetailView.as_view(), name='hello2'),
	path('stores/', StoreDetailView.as_view(), name='hello2'),
	path('stores/logo/<int:store_id>', StoreImageChangeView.as_view(), name='Hello3'),
	path('items/logo/<int:storeitem_id>', StoreItemImageChangeView.as_view(), name='Hello3'),
	path('stores/<int:store_id>/items', StoreItemsView.as_view(), name='Hello4'),
	path('stores/<int:store_id>/item/<int:storeitem_id>', CreateOrUpdateStoreItemsView.as_view(), name='Hello5'),
	path('stores/<int:store_id>/item', CreateOrUpdateStoreItemsView2.as_view(), name='Hello7'),
	path('cart',CartItemsView.as_view(), name='Hello6'),
	path('doOrder',OrderProcess.as_view(),name='Hello 7'),
	path('itemRecommendation/<int:store_id>/<int:nos_recommendations>',RecommendationView.as_view(),name='Hello 7'),
	path('storeRecommendation/<int:nos_recommendations>',StoreRecommendationView.as_view(),name='Hello 8'),

]