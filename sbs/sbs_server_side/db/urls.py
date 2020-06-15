from django.conf.urls import url
from db import views
from django.urls import path

app_name = 'db'

urlpatterns = [
   path('',views.loginPage,name = 'loginPage'),
   path('user_login',views.user_login, name = 'user_login'),
   path('user_logout', views.user_logout, name = 'user_logout'),
]