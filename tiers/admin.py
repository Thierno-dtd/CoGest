from django.contrib import admin
from .models import Client, Fournisseur


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'type_client', 'telephone', 'email', 'est_actif')
    search_fields = ('nom', 'prenom', 'telephone', 'email')


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'telephone', 'email', 'delai_livraison_moyen_jours', 'est_actif')
    search_fields = ('raison_sociale', 'telephone', 'email')
