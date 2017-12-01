from django.conf.urls import include, url
from . import views

app_name = 'hybridapp'

urlpatterns = [
    url(r'^$', views.home, name='main'),
    url(r'^home/$', views.home, name='home'),
]
