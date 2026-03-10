from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('room/<uuid:code>/', views.room, name='room'),
    path('api/check-room/<uuid:code>/', views.check_room, name='check_room'),
]
