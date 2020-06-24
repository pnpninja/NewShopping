from django.urls import include,path
#from .views import CustomUserListView, CustomUserDetailView, PersonalUserDetailView
from .views import PersonalUserDetailView

urlpatterns = [
	#path('',CustomUserListView.as_view()),
	#path('<pk>',CustomUserDetailView.as_view()),
	path('userdetails', PersonalUserDetailView.as_view(), name='hello'),
#	path('userdetails')

]