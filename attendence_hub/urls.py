
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login,name="login"),
    path('logout/', logout, name='logout'), 
    path('active/', active,name="active"),
    path('active_data_save/', active_data_save,name="active_data_save"),
    path('deactive/', deactive,name="deactive"),
    path('deactive-data-save/', deactive_data_save, name='deactive_data_save'),
    path('breakin-data-save/', breakin_data_save, name='breakin_data_save'),
    path('breakout-data-save/', breakout_data_save, name='breakout_data_save'),
]
