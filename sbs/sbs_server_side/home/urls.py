from django.conf.urls import url
from django.urls import path, include
from home import views
from home.models import Record

app_name = 'home'

urlpatterns = [
     path('<req_status>/',views.homePage,name = 'homePage'),
     path('',include('req.urls')),
]
