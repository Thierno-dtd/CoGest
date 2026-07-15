from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, Count
from django.shortcuts import render

from core.pagination import paginer
from .models import MouvementStock
from produits.models import Produit


@login_required
def mouvement_liste(request):
    q = request.GET.get('q', '').strip()
    type_mouvement = request.GET.get('type', '')

    mouvements = MouvementStock.objects.select_related('produit', 'utilisateur').all()
    if q:
        mouvements = mouvements.filter(
            Q(produit__reference__icontains=q) | Q(produit__designation__icontains=q) | Q(id_document_origine__icontains=q)
        )
    if type_mouvement:
        mouvements = mouvements.filter(type_mouvement=type_mouvement)

    page_obj = paginer(request, mouvements, 15)

    stats_stock = Produit.objects.aggregate(
        valeur_totale=Sum(F('quantite_stock') * F('prix_achat')),
        qte_totale=Sum('quantite_stock'),
    )
    stats = {
        'valeur_totale': stats_stock['valeur_totale'] or 0,
        'qte_totale': stats_stock['qte_totale'] or 0,
        'ruptures': Produit.objects.filter(quantite_stock__lte=0, est_actif=True).count(),
        'entrees_total': MouvementStock.objects.filter(type_mouvement=MouvementStock.TypeMouvement.ENTREE).count(),
        'sorties_total': MouvementStock.objects.filter(type_mouvement=MouvementStock.TypeMouvement.SORTIE).count(),
    }
    template = 'stock/_mouvement_table.html' if request.htmx else 'stock/mouvement_liste.html'
    return render(request, template, {'page_obj': page_obj, 'q': q, 'type_mouvement': type_mouvement, 'stats': stats})
