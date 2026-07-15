from django.urls import path
from . import views

app_name = 'produits'

urlpatterns = [
    path('', views.produit_liste, name='produit_liste'),
    path('nouveau/', views.produit_creer, name='produit_creer'),
    path('<int:pk>/', views.produit_detail, name='produit_detail'),
    path('<int:pk>/modifier/', views.produit_modifier, name='produit_modifier'),
    path('<int:pk>/supprimer/', views.produit_supprimer, name='produit_supprimer'),

    path('categories/', views.categorie_liste, name='categorie_liste'),
    path('categories/nouvelle/', views.categorie_creer, name='categorie_creer'),
    path('categories/<int:pk>/modifier/', views.categorie_modifier, name='categorie_modifier'),
    path('categories/<int:pk>/supprimer/', views.categorie_supprimer, name='categorie_supprimer'),
]
