from django.conf import settings
from django.db import models
from django.urls import reverse


class Vente(models.Model):
    class Statut(models.TextChoices):
        EN_COURS = 'EN_COURS', 'En cours'
        VALIDEE = 'VALIDEE', 'Validée'
        ANNULEE = 'ANNULEE', 'Annulée'

    numero = models.CharField(max_length=30, unique=True, editable=False)
    client = models.ForeignKey('tiers.Client', on_delete=models.PROTECT, related_name='ventes')
    date_vente = models.DateField()
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ventes_realisees')
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.VALIDEE)
    date_creation = models.DateTimeField(auto_now_add=True)
    total_ht_cache = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_tva_cache = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_ttc_cache = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ['-date_vente', '-id']
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"

    def __str__(self):
        return self.numero

    def get_absolute_url(self):
        return reverse('ventes:vente_detail', args=[self.pk])

    def recalculer_totaux(self, save=True):
        ht = tva = ttc = 0
        for ligne in self.lignes.all():
            ht += ligne.montant_ht
            tva += ligne.montant_tva
            ttc += ligne.montant_ttc
        self.total_ht_cache = ht
        self.total_tva_cache = tva
        self.total_ttc_cache = ttc
        if save:
            self.save(update_fields=['total_ht_cache', 'total_tva_cache', 'total_ttc_cache'])
        return ht, tva, ttc


class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey('produits.Produit', on_delete=models.PROTECT, related_name='lignes_vente')
    quantite_vendue = models.PositiveIntegerField()
    prix_vente_unitaire_applique = models.DecimalField(max_digits=14, decimal_places=2)
    taux_tva_applique = models.DecimalField(max_digits=4, decimal_places=2)
    remise_pourcentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Ligne de vente"
        verbose_name_plural = "Lignes de vente"

    def __str__(self):
        return f"{self.produit.designation} x{self.quantite_vendue}"

    @property
    def montant_brut(self):
        return self.quantite_vendue * self.prix_vente_unitaire_applique

    @property
    def montant_remise(self):
        return self.montant_brut * (self.remise_pourcentage / 100)

    @property
    def montant_ht(self):
        return self.montant_brut - self.montant_remise

    @property
    def montant_tva(self):
        return self.montant_ht * self.taux_tva_applique

    @property
    def montant_ttc(self):
        return self.montant_ht + self.montant_tva
