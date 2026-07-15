from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core.pagination import paginer
from .models import Facture, Reglement
from .forms import ReglementForm
from .pdf import generer_pdf_facture


@login_required
def facture_liste(request):
    q = request.GET.get('q', '').strip()
    type_facture = request.GET.get('type', '')
    etat = request.GET.get('etat', '')

    factures = Facture.objects.select_related('achat__fournisseur', 'vente__client').all()
    if type_facture:
        factures = factures.filter(type_facture=type_facture)
    if q:
        factures = factures.filter(
            Q(numero__icontains=q) | Q(achat__fournisseur__raison_sociale__icontains=q) |
            Q(vente__client__nom__icontains=q) | Q(vente__client__prenom__icontains=q)
        )

    factures = list(factures)
    if etat == 'soldee':
        factures = [f for f in factures if f.est_soldee]
    elif etat == 'non_soldee':
        factures = [f for f in factures if not f.est_soldee]
    elif etat == 'retard':
        factures = [f for f in factures if f.est_en_retard]

    page_obj = paginer(request, factures, 10)

    toutes = Facture.objects.select_related('achat', 'vente').all()
    creances = sum(f.solde_restant for f in toutes if f.type_facture == Facture.TypeFacture.VENTE)
    dettes = sum(f.solde_restant for f in toutes if f.type_facture == Facture.TypeFacture.ACHAT)
    encaisse = sum(f.montant_paye for f in toutes if f.type_facture == Facture.TypeFacture.VENTE)
    stats = {
        'creances_clients': creances,
        'dettes_fournisseurs': dettes,
        'encaisse': encaisse,
        'nb_retard': len([f for f in toutes if f.est_en_retard]),
    }
    template = 'facturation/_facture_table.html' if request.htmx else 'facturation/facture_liste.html'
    return render(request, template, {'page_obj': page_obj, 'q': q, 'type_facture': type_facture, 'etat': etat, 'stats': stats})


@login_required
def facture_detail(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        form = ReglementForm(request.POST)
        if form.is_valid():
            reglement = form.save(commit=False)
            reglement.facture = facture
            reglement.utilisateur = request.user
            if reglement.montant_verse > facture.solde_restant:
                messages.error(request, "Le montant versé dépasse le solde restant de la facture.")
            else:
                reglement.save()
                messages.success(request, "Règlement enregistré avec succès.")
                return redirect('facturation:facture_detail', pk=facture.pk)
    else:
        form = ReglementForm(initial={'montant_verse': facture.solde_restant, 'date_paiement': timezone.localdate()})
    return render(request, 'facturation/facture_detail.html', {'facture': facture, 'form': form})


@login_required
def facture_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    buffer = generer_pdf_facture(facture)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{facture.numero}.pdf"'
    return response
