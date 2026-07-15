from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from ventes.models import Vente, LigneVente
from achats.models import Achat
from produits.models import Produit, Categorie
from tiers.models import Client, Fournisseur
from facturation.models import Facture
from stock.models import MouvementStock


@login_required
def accueil(request):
    aujourdhui = timezone.localdate()
    debut_mois = aujourdhui.replace(day=1)
    debut_mois_prec = (debut_mois - timedelta(days=1)).replace(day=1)

    ca_mois = Vente.objects.filter(date_vente__gte=debut_mois, statut=Vente.Statut.VALIDEE).aggregate(t=Sum('total_ttc_cache'))['t'] or 0
    ca_mois_prec = Vente.objects.filter(date_vente__gte=debut_mois_prec, date_vente__lt=debut_mois, statut=Vente.Statut.VALIDEE).aggregate(t=Sum('total_ttc_cache'))['t'] or 0
    evolution_ca = 0
    if ca_mois_prec:
        evolution_ca = round((float(ca_mois) - float(ca_mois_prec)) / float(ca_mois_prec) * 100, 1)

    achats_mois = Achat.objects.filter(date_achat__gte=debut_mois).aggregate(t=Sum('total_ttc_cache'))['t'] or 0

    toutes_factures = Facture.objects.all()
    creances = sum(f.solde_restant for f in toutes_factures if f.type_facture == Facture.TypeFacture.VENTE)
    dettes = sum(f.solde_restant for f in toutes_factures if f.type_facture == Facture.TypeFacture.ACHAT)

    valeur_stock = Produit.objects.aggregate(v=Sum(F('quantite_stock') * F('prix_achat')))['v'] or 0
    ruptures = Produit.objects.filter(quantite_stock__lte=0, est_actif=True).count()
    alertes = Produit.objects.filter(quantite_stock__gt=0, quantite_stock__lte=F('seuil_alerte'), est_actif=True).count()

    kpis = {
        'ca_mois': ca_mois,
        'evolution_ca': evolution_ca,
        'nb_ventes_mois': Vente.objects.filter(date_vente__gte=debut_mois, statut=Vente.Statut.VALIDEE).count(),
        'achats_mois': achats_mois,
        'creances_clients': creances,
        'dettes_fournisseurs': dettes,
        'valeur_stock': valeur_stock,
        'ruptures': ruptures,
        'alertes': alertes,
        'nb_clients': Client.objects.filter(est_actif=True).count(),
        'nb_fournisseurs': Fournisseur.objects.filter(est_actif=True).count(),
        'nb_produits': Produit.objects.filter(est_actif=True).count(),
    }
    return render(request, 'dashboard/accueil.html', {'kpis': kpis})


def _bornes_periode(periode):
    aujourdhui = timezone.localdate()
    if periode == '7j':
        return aujourdhui - timedelta(days=7), 'jour'
    if periode == '90j':
        return aujourdhui - timedelta(days=90), 'jour'
    if periode == '12m':
        return aujourdhui - timedelta(days=365), 'mois'
    return aujourdhui - timedelta(days=30), 'jour'


@login_required
def api_ventes_achats(request):
    periode = request.GET.get('periode', '30j')
    debut, granularite = _bornes_periode(periode)

    ventes_brutes = (Vente.objects.filter(date_vente__gte=debut, statut=Vente.Statut.VALIDEE)
                      .values('date_vente').annotate(total=Sum('total_ttc_cache')))
    achats_bruts = (Achat.objects.filter(date_achat__gte=debut)
                     .values('date_achat').annotate(total=Sum('total_ttc_cache')))

    if granularite == 'jour':
        ventes_map = {row['date_vente']: float(row['total'] or 0) for row in ventes_brutes}
        achats_map = {row['date_achat']: float(row['total'] or 0) for row in achats_bruts}
        fmt = lambda d: d.strftime('%d/%m')
    else:
        ventes_map = {}
        for row in ventes_brutes:
            cle = row['date_vente'].replace(day=1)
            ventes_map[cle] = ventes_map.get(cle, 0) + float(row['total'] or 0)
        achats_map = {}
        for row in achats_bruts:
            cle = row['date_achat'].replace(day=1)
            achats_map[cle] = achats_map.get(cle, 0) + float(row['total'] or 0)
        fmt = lambda d: d.strftime('%b %Y')

    toutes_dates = sorted(set(ventes_map) | set(achats_map))

    return JsonResponse({
        'labels': [fmt(d) for d in toutes_dates],
        'ventes': [round(ventes_map.get(d, 0)) for d in toutes_dates],
        'achats': [round(achats_map.get(d, 0)) for d in toutes_dates],
    })


@login_required
def api_top_produits(request):
    periode = request.GET.get('periode', '30j')
    critere = request.GET.get('critere', 'quantite')
    debut, _ = _bornes_periode(periode)

    lignes = LigneVente.objects.filter(vente__date_vente__gte=debut, vente__statut=Vente.Statut.VALIDEE)
    agg = list(lignes.values('produit__designation')
               .annotate(quantite=Sum('quantite_vendue'),
                         ca=Sum(F('quantite_vendue') * F('prix_vente_unitaire_applique'))))

    if critere == 'rentabilite':
        agg = sorted(agg, key=lambda r: r['ca'] or 0, reverse=True)[:8]
        valeurs = [round(float(r['ca'] or 0)) for r in agg]
    elif critere == 'moins_vendus':
        agg = sorted(agg, key=lambda r: r['quantite'] or 0)[:8]
        valeurs = [r['quantite'] or 0 for r in agg]
    else:
        agg = sorted(agg, key=lambda r: r['quantite'] or 0, reverse=True)[:8]
        valeurs = [r['quantite'] or 0 for r in agg]

    return JsonResponse({
        'labels': [r['produit__designation'] for r in agg],
        'valeurs': valeurs,
        'critere': critere,
    })


@login_required
def api_repartition_categories(request):
    data = (Produit.objects.filter(est_actif=True)
            .values('categorie__libelle')
            .annotate(valeur=Sum(F('quantite_stock') * F('prix_achat')))
            .order_by('-valeur'))
    return JsonResponse({
        'labels': [d['categorie__libelle'] or 'Non classé' for d in data],
        'valeurs': [round(float(d['valeur'] or 0)) for d in data],
    })


@login_required
def api_clients_fideles(request):
    critere = request.GET.get('critere', 'nb_achats')
    data = list(Vente.objects.filter(statut=Vente.Statut.VALIDEE)
                .values('client__nom', 'client__prenom')
                .annotate(nb=Count('id'), ca=Sum('total_ttc_cache')))
    if critere == 'chiffre_affaires':
        data = sorted(data, key=lambda r: r['ca'] or 0, reverse=True)[:8]
        valeurs = [round(float(r['ca'] or 0)) for r in data]
    else:
        data = sorted(data, key=lambda r: r['nb'], reverse=True)[:8]
        valeurs = [r['nb'] for r in data]
    labels = [f"{r['client__prenom']} {r['client__nom']}".strip() for r in data]
    return JsonResponse({'labels': labels, 'valeurs': valeurs, 'critere': critere})


@login_required
def api_fournisseurs_sollicites(request):
    data = (Achat.objects.values('fournisseur__raison_sociale')
            .annotate(nb=Count('id'), total=Sum('total_ttc_cache'))
            .order_by('-nb')[:8])
    return JsonResponse({
        'labels': [d['fournisseur__raison_sociale'] for d in data],
        'valeurs': [d['nb'] for d in data],
    })
