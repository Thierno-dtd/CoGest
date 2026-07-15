from django.conf import settings
from django.db import models
from django.urls import reverse


class Achat(models.Model):
    class StatutLivraison(models.TextChoices):
        EN_ATTENTE = 'ATTENTE', 'En attente'
        PARTIELLE = 'PARTIELLE', 'Partielle'
        RECUE = 'RECUE', 'Reçue'
        ANNULEE = 'ANNULEE', 'Annulée'

    numero = models.CharField(max_length=30, unique=True, editable=False)
    fournisseur = models.ForeignKey('tiers.Fournisseur', on_delete=models.PROTECT, related_name='achats')
    date_achat = models.DateField()
    date_livraison_prevue = models.DateField(null=True, blank=True)
    statut_livraison = models.CharField(max_length=12, choices=StatutLivraison.choices, default=StatutLivraison.EN_ATTENTE)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='achats_saisis')
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    # Cache de performance (recalculé automatiquement, jamais saisi à la main)
    total_ht_cache = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_tva_cache = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_ttc_cache = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ['-date_achat', '-id']
        verbose_name = "Achat"
        verbose_name_plural = "Achats"

    def __str__(self):
        return self.numero

    def get_absolute_url(self):
        return reverse('achats:achat_detail', args=[self.pk])

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


class LigneAchat(models.Model):
    achat = models.ForeignKey(Achat, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey('produits.Produit', on_delete=models.PROTECT, related_name='lignes_achat')
    quantite_achetee = models.PositiveIntegerField()
    prix_achat_unitaire_applique = models.DecimalField(max_digits=14, decimal_places=2)
    taux_tva_applique = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        verbose_name = "Ligne d'achat"
        verbose_name_plural = "Lignes d'achat"

    def __str__(self):
        return f"{self.produit.designation} x{self.quantite_achetee}"

    @property
    def montant_ht(self):
        return self.quantite_achetee * self.prix_achat_unitaire_applique

    @property
    def montant_tva(self):
        return self.montant_ht * self.taux_tva_applique

    @property
    def montant_ttc(self):
        return self.montant_ht + self.montant_tva
