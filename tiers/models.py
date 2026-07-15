from django.db import models
from django.urls import reverse


class Client(models.Model):
    class TypeClient(models.TextChoices):
        PARTICULIER = 'PARTICULIER', 'Particulier'
        ENTREPRISE = 'ENTREPRISE', 'Entreprise'

    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    date_inscription = models.DateField(auto_now_add=True)
    type_client = models.CharField(max_length=15, choices=TypeClient.choices, default=TypeClient.PARTICULIER)
    plafond_credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    est_actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['nom', 'prenom']
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.nom_complet

    @property
    def nom_complet(self):
        if self.type_client == self.TypeClient.ENTREPRISE:
            return self.nom
        return f"{self.prenom} {self.nom}".strip()

    def get_absolute_url(self):
        return reverse('tiers:client_detail', args=[self.pk])

    @property
    def initiales(self):
        parts = (self.prenom[:1] + self.nom[:1]) if self.prenom else self.nom[:2]
        return parts.upper()

    @property
    def chiffre_affaires(self):
        from django.db.models import Sum
        from ventes.models import Vente
        total = self.ventes.filter(statut=Vente.Statut.VALIDEE).aggregate(t=Sum('total_ttc_cache'))['t']
        return total or 0

    @property
    def nb_achats(self):
        from ventes.models import Vente
        return self.ventes.filter(statut=Vente.Statut.VALIDEE).count()

    @property
    def encours_credit(self):
        """Somme des soldes restants sur les factures de vente non soldées."""
        total = 0
        for vente in self.ventes.all():
            f = getattr(vente, 'facture', None)
            if f and not f.est_soldee:
                total += f.solde_restant
        return total


class Fournisseur(models.Model):
    raison_sociale = models.CharField(max_length=200)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    contact_principal = models.CharField(max_length=150, blank=True)
    delai_livraison_moyen_jours = models.PositiveIntegerField(default=7)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['raison_sociale']
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"

    def __str__(self):
        return self.raison_sociale

    def get_absolute_url(self):
        return reverse('tiers:fournisseur_detail', args=[self.pk])

    @property
    def initiales(self):
        return self.raison_sociale[:2].upper()

    @property
    def montant_total_achats(self):
        from django.db.models import Sum
        total = self.achats.aggregate(t=Sum('total_ttc_cache'))['t']
        return total or 0

    @property
    def nb_achats(self):
        return self.achats.count()

    @property
    def dette_fournisseur(self):
        total = 0
        for achat in self.achats.all():
            f = getattr(achat, 'facture', None)
            if f and not f.est_soldee:
                total += f.solde_restant
        return total
