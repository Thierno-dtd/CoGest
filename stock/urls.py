from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.mouvement_liste, name='mouvement_liste'),
]
