from django.conf.urls import url
from django.urls import path, include
from home import views

app_name = 'home'

urlpatterns = [
     path('<req_status>/',views.homePage,name = 'homePage'),
     path('',include('req.urls'))
]
