from django.contrib import admin
from .models import Achat, LigneAchat


class LigneAchatInline(admin.TabularInline):
    model = LigneAchat
    extra = 0


@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fournisseur', 'date_achat', 'statut_livraison', 'total_ttc_cache')
    list_filter = ('statut_livraison',)
    inlines = [LigneAchatInline]
