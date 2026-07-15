from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class Facture(models.Model):
    class TypeFacture(models.TextChoices):
        ACHAT = 'ACHAT', 'Achat'
        VENTE = 'VENTE', 'Vente'

    numero = models.CharField(max_length=30, unique=True, editable=False)
    type_facture = models.CharField(max_length=10, choices=TypeFacture.choices)
    achat = models.OneToOneField('achats.Achat', on_delete=models.CASCADE, null=True, blank=True, related_name='facture')
    vente = models.OneToOneField('ventes.Vente', on_delete=models.CASCADE, null=True, blank=True, related_name='facture')
    date_facturation = models.DateField(auto_now_add=True)
    date_echeance = models.DateField()

    class Meta:
        ordering = ['-date_facturation', '-id']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        return self.numero

    def get_absolute_url(self):
        return reverse('facturation:facture_detail', args=[self.pk])

    @property
    def source(self):
        return self.achat if self.type_facture == self.TypeFacture.ACHAT else self.vente

    @property
    def tiers(self):
        if self.type_facture == self.TypeFacture.ACHAT:
            return self.achat.fournisseur if self.achat else None
        return self.vente.client if self.vente else None

    @property
    def lignes(self):
        return self.source.lignes.all() if self.source else []

    # --- Montants calculés dynamiquement à partir des lignes (jamais stockés en dur) ---
    @property
    def montant_ht(self):
        return sum((l.montant_ht for l in self.lignes), 0)

    @property
    def montant_tva(self):
        return sum((l.montant_tva for l in self.lignes), 0)

    @property
    def montant_ttc(self):
        return self.montant_ht + self.montant_tva

    @property
    def montant_paye(self):
        total = self.reglements.aggregate(models.Sum('montant_verse'))['montant_verse__sum']
        return total or 0

    @property
    def solde_restant(self):
        return self.montant_ttc - self.montant_paye

    @property
    def est_soldee(self):
        return self.solde_restant <= 0.01

    @property
    def est_en_retard(self):
        return (not self.est_soldee) and self.date_echeance < timezone.localdate()

    @property
    def pourcentage_paye(self):
        if self.montant_ttc:
            return min(100, round(float(self.montant_paye) / float(self.montant_ttc) * 100))
        return 100


class Reglement(models.Model):
    class ModePaiement(models.TextChoices):
        ESPECES = 'ESPECES', 'Espèces'
        CHEQUE = 'CHEQUE', 'Chèque'
        CARTE = 'CARTE', 'Carte'
        VIREMENT = 'VIREMENT', 'Virement'
        MOBILE_MONEY = 'MOBILE', 'Mobile Money'

    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='reglements')
    date_paiement = models.DateField(default=timezone.localdate)
    montant_verse = models.DecimalField(max_digits=14, decimal_places=2)
    mode_paiement = models.CharField(max_length=10, choices=ModePaiement.choices, default=ModePaiement.ESPECES)
    numero_transaction = models.CharField(max_length=100, blank=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reglements_saisis')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_paiement', '-id']
        verbose_name = "Règlement"
        verbose_name_plural = "Règlements"

    def __str__(self):
        return f"Règlement {self.montant_verse} sur {self.facture.numero}"
