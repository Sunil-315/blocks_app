from django.urls import path
from . import views

app_name = 'blocks'

urlpatterns = [
    path('', views.game, name='game'),
]
