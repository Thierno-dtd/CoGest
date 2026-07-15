from django.db import models
from django.urls import reverse
from django.conf import settings


class Categorie(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['libelle']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.libelle

    def get_absolute_url(self):
        return reverse('produits:categorie_liste')

    @property
    def nb_produits(self):
        return self.produits.filter(est_actif=True).count()


class Produit(models.Model):
    class UniteMesure(models.TextChoices):
        UNITE = 'UNITE', 'Unité'
        KG = 'KG', 'Kilogramme'
        LITRE = 'LITRE', 'Litre'
        CARTON = 'CARTON', 'Carton'
        SAC = 'SAC', 'Sac'

    reference = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name='produits')
    prix_achat = models.DecimalField(max_digits=14, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=14, decimal_places=2)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=5)
    taux_tva = models.DecimalField(max_digits=4, decimal_places=2, default=0.18)
    unite_mesure = models.CharField(max_length=10, choices=UniteMesure.choices, default=UniteMesure.UNITE)
    code_barre = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return f"{self.reference} — {self.designation}"

    def get_absolute_url(self):
        return reverse('produits:produit_detail', args=[self.pk])

    @property
    def marge_unitaire(self):
        return self.prix_vente - self.prix_achat

    @property
    def marge_pourcentage(self):
        if self.prix_achat:
            return round((self.marge_unitaire / self.prix_achat) * 100, 1)
        return 0

    @property
    def valeur_stock(self):
        return self.quantite_stock * self.prix_achat

    @property
    def en_rupture(self):
        return self.quantite_stock <= 0

    @property
    def proche_seuil(self):
        return 0 < self.quantite_stock <= self.seuil_alerte

    @property
    def statut_stock(self):
        if self.en_rupture:
            return 'rupture'
        if self.proche_seuil:
            return 'alerte'
        return 'ok'
