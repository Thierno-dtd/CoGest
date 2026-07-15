from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """
    Représente le personnel utilisant l'application.
    Django gère nativement mot_de_passe_hash (password) + sel (intégré au hash PBKDF2),
    est_actif (is_active) et date_derniere_connexion (last_login).
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        VENDEUR = 'VENDEUR', 'Vendeur'
        GESTIONNAIRE_STOCK = 'STOCK', 'Gestionnaire Stock'
        COMPTABLE = 'COMPTABLE', 'Comptable'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VENDEUR)
    telephone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_creation = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def initiales(self):
        base = (self.first_name[:1] + self.last_name[:1]).upper()
        return base or self.username[:2].upper()

    def peut_administrer(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def peut_gerer_stock(self):
        return self.role in (self.Role.ADMIN, self.Role.GESTIONNAIRE_STOCK) or self.is_superuser

    def peut_vendre(self):
        return self.role in (self.Role.ADMIN, self.Role.VENDEUR) or self.is_superuser

    def peut_comptabiliser(self):
        return self.role in (self.Role.ADMIN, self.Role.COMPTABLE) or self.is_superuser
