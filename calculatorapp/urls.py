from django.urls import path,include
from django.conf.urls import url


from . import views

urlpatterns = [
    path('',views.homepage,name='home'),
    path('data/', views.receivedata, name='vector'),
    path('call/', views.senddata, name='send'),
    path('test/', views.test, name='send'),
  
    
    url(r'^raster/', include('raster.urls')),
   
]