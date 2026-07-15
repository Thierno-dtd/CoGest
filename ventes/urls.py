from django.urls import path
from . import views

app_name = 'ventes'

urlpatterns = [
    path('', views.vente_liste, name='vente_liste'),
    path('nouvelle/', views.vente_creer, name='vente_creer'),
    path('<int:pk>/', views.vente_detail, name='vente_detail'),
    path('<int:pk>/annuler/', views.vente_annuler, name='vente_annuler'),
]
