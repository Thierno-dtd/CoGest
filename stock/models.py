from django.conf import settings
from django.db import models


class MouvementStock(models.Model):
    class TypeMouvement(models.TextChoices):
        ENTREE = 'ENTREE', 'Entrée (Achat)'
        SORTIE = 'SORTIE', 'Sortie (Vente)'
        CORRECTION = 'CORRECTION', 'Correction inventaire'

    produit = models.ForeignKey('produits.Produit', on_delete=models.PROTECT, related_name='mouvements')
    type_mouvement = models.CharField(max_length=12, choices=TypeMouvement.choices)
    quantite = models.IntegerField()
    date_mouvement = models.DateTimeField(auto_now_add=True)
    id_document_origine = models.CharField(max_length=50, blank=True)
    quantite_avant = models.IntegerField()
    quantite_apres = models.IntegerField()
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='mouvements_stock')
    motif = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['-date_mouvement']
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"

    def __str__(self):
        return f"{self.get_type_mouvement_display()} — {self.produit.reference} ({self.quantite})"
