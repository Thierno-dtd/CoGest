from django.contrib import admin
from .models import Vente, LigneVente


class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 0


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'client', 'date_vente', 'statut', 'total_ttc_cache')
    list_filter = ('statut',)
    inlines = [LigneVenteInline]
