from django.urls import include,path
from .views_user import PersonalUserDetailView, StoreDetailView, StoreImageChangeView

urlpatterns = [
	path('users/userdetails', PersonalUserDetailView.as_view(), name='hello'),
	path('stores/<int:store_id>', StoreDetailView.as_view(), name='hello2'),
	path('stores/', StoreDetailView.as_view(), name='hello2'),
	path('stores/logo/<int:store_id>', StoreImageChangeView.as_view(), name='Hello3')
	path('items')
]