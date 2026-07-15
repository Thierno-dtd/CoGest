from django.contrib import admin
from .models import Categorie, Produit


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'nb_produits', 'est_active')
    search_fields = ('libelle',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('reference', 'designation', 'categorie', 'prix_achat', 'prix_vente', 'quantite_stock', 'est_actif')
    list_filter = ('categorie', 'est_actif')
    search_fields = ('reference', 'designation', 'code_barre')
