from django.urls import path
from drrr import views

urlpatterns = [
    path('login', views.login),
    path('room_list', views.room_list),
]
