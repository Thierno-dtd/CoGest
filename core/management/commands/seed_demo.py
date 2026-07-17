import io
import random
from datetime import timedelta, date

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from accounts.models import Utilisateur
from produits.models import Categorie, Produit
from tiers.models import Client, Fournisseur
from core.services import creer_achat, creer_vente
from facturation.models import Reglement


# Palette cohérente avec le design system (une couleur par catégorie, cycle si besoin)
PALETTE_IMAGES = ["#B4602E", "#1C1A17", "#3E7A52", "#35618A", "#984E23", "#7C766B"]


def generer_image_produit(designation, index_categorie):
    """
    Génère une vignette placeholder (aucune dépendance réseau) : fond coloré selon la
    catégorie + initiales du produit, dans le même esprit graphique que l'application.
    Retourne un ContentFile PNG prêt à être assigné à Produit.image.
    """
    couleur = PALETTE_IMAGES[index_categorie % len(PALETTE_IMAGES)]
    img = Image.new("RGB", (480, 480), couleur)
    draw = ImageDraw.Draw(img)

    mots = designation.split()
    initiales = "".join(m[0] for m in mots[:2]).upper()

    try:
        police = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 160)
    except OSError:
        police = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), initiales, font=police)
    largeur_texte = bbox[2] - bbox[0]
    hauteur_texte = bbox[3] - bbox[1]
    position = ((480 - largeur_texte) / 2 - bbox[0], (480 - hauteur_texte) / 2 - bbox[1])
    draw.text(position, initiales, fill="#FBF9F4", font=police)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f"{initiales.lower()}-{random.randint(1000,9999)}.png")


NOMS = ["Ondo", "Mba", "Nzue", "Obame", "Ella", "Moussavou", "Ndong", "Ovono", "Boukandou", "Mengue",
        "Ntoutoume", "Ogandaga", "Ibinga", "Nzamba", "Assoumou", "Koumba", "Bivigou", "Meye", "Nziengui"]
PRENOMS_F = ["Sylvie", "Nadège", "Carine", "Pauline", "Judith", "Aïcha", "Stéphanie", "Sandrine"]
PRENOMS_H = ["Jean", "Pierre", "Serge", "Aristide", "Brice", "Landry", "Thierry", "Cédric", "Yannick"]
QUARTIERS = ["Akanda", "Nzeng-Ayong", "Lalala", "Glass", "Louis", "Batterie IV", "Nombakélé",
             "Charbonnages", "Oloumi", "PK8", "PK12", "Awendjé"]


class Command(BaseCommand):
    help = "Génère un jeu de données de démonstration réaliste (contexte Libreville, Gabon)."

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help="Vide les données transactionnelles avant de regénérer.")

    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write(self.style.NOTICE("Génération des données de démonstration…"))

        self._creer_utilisateurs()
        categories = self._creer_categories()
        produits = self._creer_produits(categories)
        clients = self._creer_clients()
        fournisseurs = self._creer_fournisseurs()
        self._creer_achats(fournisseurs, produits)
        self._creer_ventes(clients, produits)
        self._creer_reglements_partiels()

        self.stdout.write(self.style.SUCCESS("Jeu de données généré avec succès !"))
        self.stdout.write(self.style.SUCCESS("Connexion admin → identifiant : admin / mot de passe : admin1234"))

    def _creer_utilisateurs(self):
        if not Utilisateur.objects.filter(username='admin').exists():
            Utilisateur.objects.create_superuser('admin', 'admin@gestion-commerciale.ga', 'admin1234',
                                                  first_name='Thierno', last_name='Diallo', role=Utilisateur.Role.ADMIN)
        comptes = [
            ('vendeur1', 'Aïsha', 'Nzue', Utilisateur.Role.VENDEUR),
            ('stock1', 'Landry', 'Ovono', Utilisateur.Role.GESTIONNAIRE_STOCK),
            ('compta1', 'Judith', 'Mengue', Utilisateur.Role.COMPTABLE),
        ]
        for username, prenom, nom, role in comptes:
            if not Utilisateur.objects.filter(username=username).exists():
                u = Utilisateur.objects.create_user(username, f"{username}@gestion-commerciale.ga", "passer1234",
                                                     first_name=prenom, last_name=nom, role=role)
                u.save()
        self.stdout.write("  → Utilisateurs créés (admin / vendeur1 / stock1 / compta1, mot de passe : admin1234 ou passer1234)")

    def _creer_categories(self):
        libelles = [
            ("Alimentation générale", "Riz, huile, conserves, boissons"),
            ("Boissons", "Sodas, jus, eaux minérales, bières"),
            ("Hygiène & Beauté", "Savons, cosmétiques, produits d'entretien"),
            ("Électronique", "Téléphonie, accessoires, petit électroménager"),
            ("Quincaillerie", "Outillage, matériaux de construction"),
            ("Textile", "Vêtements, pagnes, chaussures"),
        ]
        categories = []
        for lib, desc in libelles:
            cat, _ = Categorie.objects.get_or_create(libelle=lib, defaults={'description': desc})
            categories.append(cat)
        self.stdout.write(f"  → {len(categories)} catégories créées")
        return categories

    def _creer_produits(self, categories):
        catalogue = [
            ("Riz parfumé 25kg", 0, 15500, 19000, 5),
            ("Huile végétale 5L", 0, 8200, 10500, 8),
            ("Sucre en poudre 1kg", 0, 900, 1300, 20),
            ("Farine de blé 1kg", 0, 700, 1100, 15),
            ("Sardines à l'huile (boîte)", 0, 550, 850, 30),
            ("Lait en poudre 900g", 0, 3200, 4200, 10),
            ("Coca-Cola 1.5L", 1, 850, 1200, 24),
            ("Régab 65cl (casier)", 1, 9500, 12000, 10),
            ("Eau minérale 1.5L", 1, 400, 650, 30),
            ("Jus de fruits local 1L", 1, 1200, 1800, 12),
            ("Savon de Marseille (lot 3)", 2, 1500, 2200, 15),
            ("Crème hydratante Nivea", 2, 2800, 3900, 10),
            ("Détergent liquide 1L", 2, 1400, 2100, 12),
            ("Papier toilette (pack 6)", 2, 1800, 2600, 15),
            ("Câble USB-C 1m", 3, 1500, 2800, 20),
            ("Écouteurs Bluetooth", 3, 8500, 14000, 6),
            ("Powerbank 10000mAh", 3, 12000, 18500, 5),
            ("Chargeur secteur universel", 3, 3200, 5500, 10),
            ("Ciment CIMGABON 50kg", 4, 6200, 7500, 4),
            ("Peinture blanche 20L", 4, 22000, 28000, 3),
            ("Tôle bac aluminium 3m", 4, 9800, 12500, 6),
            ("Pagne Wax 6 yards", 5, 9500, 15000, 5),
            ("T-shirt coton (unité)", 5, 2200, 4000, 15),
            ("Sandales plastique", 5, 1800, 3200, 10),
        ]
        produits = []
        for i, (designation, cat_idx, achat, vente, seuil) in enumerate(catalogue, start=1):
            ref = f"PRD-{i:04d}"
            stock_initial = random.randint(seuil + 5, seuil * 6 + 20)
            produit, cree = Produit.objects.get_or_create(
                reference=ref,
                defaults=dict(
                    designation=designation, categorie=categories[cat_idx],
                    prix_achat=achat, prix_vente=vente, quantite_stock=stock_initial,
                    seuil_alerte=seuil, taux_tva=0.18,
                )
            )
            if cree and not produit.image:
                produit.image.save(
                    f"{ref}.png",
                    generer_image_produit(designation, cat_idx),
                    save=True,
        )
            produits.append(produit)
        # Créer volontairement quelques ruptures / alertes pour la démo
        for p in produits[:2]:
            p.quantite_stock = 0
            p.save(update_fields=['quantite_stock'])
        for p in produits[2:5]:
            p.quantite_stock = max(1, p.seuil_alerte - 1)
            p.save(update_fields=['quantite_stock'])
        self.stdout.write(f"  → {len(produits)} produits créés")
        return produits

    def _creer_clients(self):
        clients = []
        for i in range(24):
            est_entreprise = i % 6 == 0
            nom = random.choice(NOMS)
            if est_entreprise:
                nom_complet = f"Établissements {nom} & Fils"
                client, _ = Client.objects.get_or_create(
                    nom=nom_complet,
                    defaults=dict(
                        type_client=Client.TypeClient.ENTREPRISE,
                        telephone=f"+241 0{random.randint(1,7)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                        email=f"contact@{nom.lower()}-gabon.ga",
                        adresse=f"Quartier {random.choice(QUARTIERS)}, Libreville",
                        plafond_credit=random.choice([500000, 1000000, 2000000]),
                    )
                )
            else:
                prenom = random.choice(PRENOMS_F + PRENOMS_H)
                client, _ = Client.objects.get_or_create(
                    nom=nom, prenom=prenom,
                    defaults=dict(
                        type_client=Client.TypeClient.PARTICULIER,
                        telephone=f"+241 0{random.randint(1,7)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                        email=f"{prenom.lower()}.{nom.lower()}@gmail.com",
                        adresse=f"Quartier {random.choice(QUARTIERS)}, Libreville",
                        plafond_credit=random.choice([0, 50000, 100000]),
                    )
                )
            clients.append(client)
        self.stdout.write(f"  → {len(clients)} clients créés")
        return clients

    def _creer_fournisseurs(self):
        noms = ["SOGATRA Distribution", "Gabon Import-Export", "CECA Gadis", "SCG Négoce",
                "Alliance Commerciale du Gabon", "Ogooué Trading", "Estuaire Logistique"]
        fournisseurs = []
        for nom in noms:
            f, _ = Fournisseur.objects.get_or_create(
                raison_sociale=nom,
                defaults=dict(
                    telephone=f"+241 0{random.randint(1,7)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                    email=f"contact@{nom.split()[0].lower()}.ga",
                    adresse=f"Zone industrielle d'Oloumi, Libreville",
                    contact_principal=f"{random.choice(PRENOMS_H)} {random.choice(NOMS)}",
                    delai_livraison_moyen_jours=random.choice([3, 5, 7, 10, 14]),
                )
            )
            fournisseurs.append(f)
        self.stdout.write(f"  → {len(fournisseurs)} fournisseurs créés")
        return fournisseurs

    def _creer_achats(self, fournisseurs, produits):
        admin = Utilisateur.objects.get(username='admin')
        aujourdhui = timezone.localdate()
        nb = 0
        for jours_avant in range(0, 200, 5):
            d = aujourdhui - timedelta(days=jours_avant)
            fournisseur = random.choice(fournisseurs)
            lignes = []
            for p in random.sample(produits, k=random.randint(1, 4)):
                lignes.append({'produit': p, 'quantite': random.randint(5, 30)})
            try:
                creer_achat(fournisseur, d, lignes, admin, statut_livraison='RECUE')
                nb += 1
            except Exception:
                pass
        self.stdout.write(f"  → {nb} achats créés (avec factures et mouvements de stock)")

    def _creer_ventes(self, clients, produits):
        admin = Utilisateur.objects.get(username='admin')
        aujourdhui = timezone.localdate()
        nb = 0
        for jours_avant in range(0, 200):
            if random.random() > 0.55:
                continue
            d = aujourdhui - timedelta(days=jours_avant)
            client = random.choice(clients)
            lignes = []
            for p in random.sample(produits, k=random.randint(1, 3)):
                if p.quantite_stock <= 0:
                    continue
                qte = min(random.randint(1, 5), max(1, p.quantite_stock))
                lignes.append({'produit': p, 'quantite': qte})
            if not lignes:
                continue
            try:
                creer_vente(client, d, lignes, admin)
                nb += 1
            except Exception:
                pass
        self.stdout.write(f"  → {nb} ventes créées (avec factures et mouvements de stock)")

    def _creer_reglements_partiels(self):
        from facturation.models import Facture
        admin = Utilisateur.objects.get(username='admin')
        nb = 0
        for facture in Facture.objects.all():
            if random.random() < 0.6:
                montant = facture.montant_ttc
                if random.random() < 0.5:
                    reglement = montant
                else:
                    reglement = round(float(montant) * random.uniform(0.3, 0.8))
                if reglement > 0:
                    Reglement.objects.create(
                        facture=facture, montant_verse=reglement,
                        mode_paiement=random.choice(['ESPECES', 'MOBILE', 'VIREMENT', 'CHEQUE']),
                        utilisateur=admin,
                        date_paiement=facture.date_facturation + timedelta(days=random.randint(0, 20)),
                    )
                    nb += 1
        self.stdout.write(f"  → {nb} règlements créés")
