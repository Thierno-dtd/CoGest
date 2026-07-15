from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core.pagination import paginer
from core.decorators import role_requis
from core.services import creer_vente, annuler_vente, StockInsuffisantError
from .models import Vente
from .forms import VenteEnteteForm, LigneVenteFormSet


@login_required
def vente_liste(request):
    q = request.GET.get('q', '').strip()
    statut = request.GET.get('statut', '')

    ventes = Vente.objects.select_related('client').all()
    if q:
        ventes = ventes.filter(Q(numero__icontains=q) | Q(client__nom__icontains=q) | Q(client__prenom__icontains=q))
    if statut:
        ventes = ventes.filter(statut=statut)

    page_obj = paginer(request, ventes, 10)

    debut_mois = timezone.localdate().replace(day=1)
    stats = {
        'ca_mois': Vente.objects.filter(date_vente__gte=debut_mois, statut=Vente.Statut.VALIDEE).aggregate(t=Sum('total_ttc_cache'))['t'] or 0,
        'nb_mois': Vente.objects.filter(date_vente__gte=debut_mois, statut=Vente.Statut.VALIDEE).count(),
        'nb_total': Vente.objects.filter(statut=Vente.Statut.VALIDEE).count(),
        'panier_moyen': 0,
    }
    if stats['nb_total']:
        total_ca = Vente.objects.filter(statut=Vente.Statut.VALIDEE).aggregate(t=Sum('total_ttc_cache'))['t'] or 0
        stats['panier_moyen'] = round(float(total_ca) / stats['nb_total'])
    template = 'ventes/_vente_table.html' if request.htmx else 'ventes/vente_liste.html'
    return render(request, template, {'page_obj': page_obj, 'q': q, 'statut': statut, 'stats': stats})


@login_required
def vente_detail(request, pk):
    vente = get_object_or_404(Vente.objects.select_related('client', 'utilisateur'), pk=pk)
    return render(request, 'ventes/vente_detail.html', {'vente': vente})


@login_required
@role_requis('peut_administrer', 'peut_vendre')
def vente_creer(request):
    if request.method == 'POST':
        entete_form = VenteEnteteForm(request.POST)
        formset = LigneVenteFormSet(request.POST)
        if entete_form.is_valid() and formset.is_valid():
            lignes_data = []
            for f in formset:
                if f.cleaned_data and not f.cleaned_data.get('DELETE'):
                    lignes_data.append({
                        'produit': f.cleaned_data['produit'],
                        'quantite': f.cleaned_data['quantite'],
                        'prix_vente_unitaire': f.cleaned_data.get('prix_vente_unitaire'),
                        'remise': f.cleaned_data.get('remise_pourcentage') or 0,
                    })
            if not lignes_data:
                messages.error(request, "Veuillez ajouter au moins une ligne d'article.")
            else:
                try:
                    vente = creer_vente(
                        client=entete_form.cleaned_data['client'],
                        date_vente=entete_form.cleaned_data['date_vente'],
                        lignes_data=lignes_data,
                        utilisateur=request.user,
                    )
                    messages.success(request, f"Vente {vente.numero} enregistrée : stock mis à jour et facture générée.")
                    return redirect('ventes:vente_detail', pk=vente.pk)
                except StockInsuffisantError as e:
                    messages.error(request, str(e))
    else:
        entete_form = VenteEnteteForm(initial={'date_vente': timezone.localdate()})
        formset = LigneVenteFormSet()
    return render(request, 'ventes/vente_form.html', {'entete_form': entete_form, 'formset': formset})


@login_required
@role_requis('peut_administrer', 'peut_vendre')
def vente_annuler(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    if request.method == 'POST':
        annuler_vente(vente, request.user)
        messages.success(request, f"Vente {vente.numero} annulée, le stock a été restitué.")
        if request.htmx:
            from django.http import HttpResponse
            resp = HttpResponse(status=204)
            resp['HX-Refresh'] = 'true'
            return resp
        return redirect('ventes:vente_detail', pk=vente.pk)
    return render(request, 'ventes/_confirmer_annulation.html', {'vente': vente})
