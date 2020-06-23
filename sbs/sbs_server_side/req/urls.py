from django.contrib import admin
from django.urls import path, include
from req import views

app_name = 'req'

urlpatterns = [
    path('',views.requestAction, name = 'requestAction'),
    path('makeRequest',views.makeRequest, name = 'makeRequest'),
    path('viewRequest/',views.viewRequests, name = 'viewRequests'),
]
