from django.urls import path
from . import views

app_name = 'tiers'

urlpatterns = [
    path('clients/', views.client_liste, name='client_liste'),
    path('clients/nouveau/', views.client_creer, name='client_creer'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/<int:pk>/modifier/', views.client_modifier, name='client_modifier'),
    path('clients/<int:pk>/supprimer/', views.client_supprimer, name='client_supprimer'),

    path('fournisseurs/', views.fournisseur_liste, name='fournisseur_liste'),
    path('fournisseurs/nouveau/', views.fournisseur_creer, name='fournisseur_creer'),
    path('fournisseurs/<int:pk>/', views.fournisseur_detail, name='fournisseur_detail'),
    path('fournisseurs/<int:pk>/modifier/', views.fournisseur_modifier, name='fournisseur_modifier'),
    path('fournisseurs/<int:pk>/supprimer/', views.fournisseur_supprimer, name='fournisseur_supprimer'),
]
