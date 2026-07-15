from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('api/ventes-achats/', views.api_ventes_achats, name='api_ventes_achats'),
    path('api/top-produits/', views.api_top_produits, name='api_top_produits'),
    path('api/repartition-categories/', views.api_repartition_categories, name='api_repartition_categories'),
    path('api/clients-fideles/', views.api_clients_fideles, name='api_clients_fideles'),
    path('api/fournisseurs-sollicites/', views.api_fournisseurs_sollicites, name='api_fournisseurs_sollicites'),
]
