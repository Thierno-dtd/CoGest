from django.contrib import admin
from .models import Facture, Reglement


class ReglementInline(admin.TabularInline):
    model = Reglement
    extra = 0


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero', 'type_facture', 'date_facturation', 'date_echeance', 'montant_ttc', 'solde_restant', 'est_soldee')
    list_filter = ('type_facture',)
    inlines = [ReglementInline]


@admin.register(Reglement)
class ReglementAdmin(admin.ModelAdmin):
    list_display = ('facture', 'date_paiement', 'montant_verse', 'mode_paiement')
