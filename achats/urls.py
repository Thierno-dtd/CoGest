from django.urls import path
from . import views

app_name = 'achats'

urlpatterns = [
    path('', views.achat_liste, name='achat_liste'),
    path('nouveau/', views.achat_creer, name='achat_creer'),
    path('<int:pk>/', views.achat_detail, name='achat_detail'),
]
