from django.contrib import admin
from .models import MouvementStock


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'type_mouvement', 'quantite', 'quantite_avant', 'quantite_apres', 'date_mouvement')
    list_filter = ('type_mouvement',)
    search_fields = ('produit__reference', 'id_document_origine')
