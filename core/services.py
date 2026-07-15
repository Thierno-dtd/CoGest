"""
Services métier centralisant les règles de gestion transversales :
- création d'un achat (+ génération facture + mouvements de stock + màj stock)
- création d'une vente (+ génération facture + mouvements de stock + màj stock)
Ceci garantit qu'aucune modification manuelle du stock n'est possible :
le stock n'est JAMAIS modifié directement, uniquement via ces services.
"""
from datetime import timedelta
from django.db import transaction
from django.utils import timezone

from core.numerotation import generer_numero
from produits.models import Produit
from stock.models import MouvementStock
from achats.models import Achat, LigneAchat
from ventes.models import Vente, LigneVente
from facturation.models import Facture


class StockInsuffisantError(Exception):
    pass


@transaction.atomic
def creer_achat(fournisseur, date_achat, lignes_data, utilisateur, date_livraison_prevue=None, notes='', statut_livraison=Achat.StatutLivraison.RECUE):
    """
    lignes_data: liste de dicts {produit, quantite, prix_achat_unitaire (optionnel), taux_tva (optionnel)}
    """
    achat = Achat.objects.create(
        numero=generer_numero('ACH', Achat),
        fournisseur=fournisseur,
        date_achat=date_achat,
        date_livraison_prevue=date_livraison_prevue,
        notes=notes,
        utilisateur=utilisateur,
        statut_livraison=statut_livraison,
    )

    for item in lignes_data:
        produit = item['produit']
        quantite = int(item['quantite'])
        prix = item.get('prix_achat_unitaire') or produit.prix_achat
        taux_tva = item.get('taux_tva')
        if taux_tva is None:
            taux_tva = produit.taux_tva

        LigneAchat.objects.create(
            achat=achat, produit=produit, quantite_achetee=quantite,
            prix_achat_unitaire_applique=prix, taux_tva_applique=taux_tva,
        )

        if statut_livraison == Achat.StatutLivraison.RECUE:
            avant = produit.quantite_stock
            produit.quantite_stock = avant + quantite
            # Le prix d'achat catalogue est actualisé au dernier prix négocié
            produit.prix_achat = prix
            produit.save(update_fields=['quantite_stock', 'prix_achat'])
            MouvementStock.objects.create(
                produit=produit, type_mouvement=MouvementStock.TypeMouvement.ENTREE,
                quantite=quantite, id_document_origine=achat.numero,
                quantite_avant=avant, quantite_apres=produit.quantite_stock,
                utilisateur=utilisateur, motif='Achat',
            )

    achat.recalculer_totaux()

    Facture.objects.create(
        numero=generer_numero('FAC-ACH', Facture),
        type_facture=Facture.TypeFacture.ACHAT,
        achat=achat,
        date_echeance=timezone.localdate() + timedelta(days=30),
    )
    return achat


@transaction.atomic
def creer_vente(client, date_vente, lignes_data, utilisateur, statut=Vente.Statut.VALIDEE):
    """
    lignes_data: liste de dicts {produit, quantite, prix_vente_unitaire (optionnel), taux_tva (optionnel), remise (optionnel)}
    Vérifie la disponibilité du stock avant toute écriture.
    """
    # Vérification préalable du stock disponible
    if statut == Vente.Statut.VALIDEE:
        for item in lignes_data:
            produit = Produit.objects.select_for_update().get(pk=item['produit'].pk)
            if produit.quantite_stock < int(item['quantite']):
                raise StockInsuffisantError(
                    f"Stock insuffisant pour « {produit.designation} » "
                    f"(disponible : {produit.quantite_stock}, demandé : {item['quantite']})."
                )

    vente = Vente.objects.create(
        numero=generer_numero('VTE', Vente),
        client=client,
        date_vente=date_vente,
        utilisateur=utilisateur,
        statut=statut,
    )

    for item in lignes_data:
        produit = item['produit']
        quantite = int(item['quantite'])
        prix = item.get('prix_vente_unitaire') or produit.prix_vente
        taux_tva = item.get('taux_tva')
        if taux_tva is None:
            taux_tva = produit.taux_tva
        remise = item.get('remise') or 0

        LigneVente.objects.create(
            vente=vente, produit=produit, quantite_vendue=quantite,
            prix_vente_unitaire_applique=prix, taux_tva_applique=taux_tva,
            remise_pourcentage=remise,
        )

        if statut == Vente.Statut.VALIDEE:
            avant = produit.quantite_stock
            produit.quantite_stock = avant - quantite
            produit.save(update_fields=['quantite_stock'])
            MouvementStock.objects.create(
                produit=produit, type_mouvement=MouvementStock.TypeMouvement.SORTIE,
                quantite=quantite, id_document_origine=vente.numero,
                quantite_avant=avant, quantite_apres=produit.quantite_stock,
                utilisateur=utilisateur, motif='Vente',
            )

    vente.recalculer_totaux()

    if statut == Vente.Statut.VALIDEE:
        Facture.objects.create(
            numero=generer_numero('FAC-VTE', Facture),
            type_facture=Facture.TypeFacture.VENTE,
            vente=vente,
            date_echeance=timezone.localdate() + timedelta(days=15),
        )
    return vente


@transaction.atomic
def annuler_vente(vente, utilisateur):
    """Annule une vente validée : restitue le stock et marque la vente comme annulée."""
    if vente.statut != Vente.Statut.VALIDEE:
        return vente
    for ligne in vente.lignes.all():
        produit = ligne.produit
        avant = produit.quantite_stock
        produit.quantite_stock = avant + ligne.quantite_vendue
        produit.save(update_fields=['quantite_stock'])
        MouvementStock.objects.create(
            produit=produit, type_mouvement=MouvementStock.TypeMouvement.CORRECTION,
            quantite=ligne.quantite_vendue, id_document_origine=vente.numero,
            quantite_avant=avant, quantite_apres=produit.quantite_stock,
            utilisateur=utilisateur, motif='Annulation vente',
        )
    vente.statut = Vente.Statut.ANNULEE
    vente.save(update_fields=['statut'])
    return vente
