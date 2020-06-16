from django.conf.urls import url
from django.urls import path
from home import views

app_name = 'home'

urlpatterns = [
     path('',views.homePage,name = 'homePage'),
]
