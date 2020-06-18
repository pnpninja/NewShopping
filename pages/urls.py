from django.urls import path
from pages import views
from .views import HomePageView

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
]