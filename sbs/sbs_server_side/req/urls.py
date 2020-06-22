from django.contrib import admin
from django.urls import path, include
from req import views

app_name = 'req'

urlpatterns = [
    path('makeRequest',views.makeRequest, name = 'makeRequest'),
    path('',views.viewRequests, name = 'viewRequests')
]
