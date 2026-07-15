from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from core.pagination import paginer
from core.decorators import role_requis
from core.services import creer_achat
from .models import Achat
from .forms import AchatEnteteForm, LigneAchatFormSet


@login_required
def achat_liste(request):
    q = request.GET.get('q', '').strip()
    statut = request.GET.get('statut', '')

    achats = Achat.objects.select_related('fournisseur').all()
    if q:
        achats = achats.filter(Q(numero__icontains=q) | Q(fournisseur__raison_sociale__icontains=q))
    if statut:
        achats = achats.filter(statut_livraison=statut)

    page_obj = paginer(request, achats, 10)

    debut_mois = timezone.localdate().replace(day=1)
    stats = {
        'total_mois': Achat.objects.filter(date_achat__gte=debut_mois).aggregate(t=Sum('total_ttc_cache'))['t'] or 0,
        'nb_mois': Achat.objects.filter(date_achat__gte=debut_mois).count(),
        'nb_total': Achat.objects.count(),
        'en_attente': Achat.objects.filter(statut_livraison=Achat.StatutLivraison.EN_ATTENTE).count(),
    }
    template = 'achats/_achat_table.html' if request.htmx else 'achats/achat_liste.html'
    return render(request, template, {'page_obj': page_obj, 'q': q, 'statut': statut, 'stats': stats})


@login_required
def achat_detail(request, pk):
    achat = get_object_or_404(Achat.objects.select_related('fournisseur', 'utilisateur'), pk=pk)
    return render(request, 'achats/achat_detail.html', {'achat': achat})


@login_required
@role_requis('peut_administrer', 'peut_gerer_stock')
def achat_creer(request):
    if request.method == 'POST':
        entete_form = AchatEnteteForm(request.POST)
        formset = LigneAchatFormSet(request.POST)
        if entete_form.is_valid() and formset.is_valid():
            lignes_data = []
            for f in formset:
                if f.cleaned_data and not f.cleaned_data.get('DELETE'):
                    lignes_data.append({
                        'produit': f.cleaned_data['produit'],
                        'quantite': f.cleaned_data['quantite'],
                        'prix_achat_unitaire': f.cleaned_data.get('prix_achat_unitaire'),
                    })
            if not lignes_data:
                messages.error(request, "Veuillez ajouter au moins une ligne d'article.")
            else:
                achat = creer_achat(
                    fournisseur=entete_form.cleaned_data['fournisseur'],
                    date_achat=entete_form.cleaned_data['date_achat'],
                    date_livraison_prevue=entete_form.cleaned_data.get('date_livraison_prevue'),
                    notes=entete_form.cleaned_data.get('notes', ''),
                    statut_livraison=entete_form.cleaned_data['statut_livraison'],
                    lignes_data=lignes_data,
                    utilisateur=request.user,
                )
                messages.success(request, f"Achat {achat.numero} enregistré : stock mis à jour et facture générée.")
                return redirect('achats:achat_detail', pk=achat.pk)
    else:
        entete_form = AchatEnteteForm(initial={'date_achat': timezone.localdate()})
        formset = LigneAchatFormSet()
    return render(request, 'achats/achat_form.html', {'entete_form': entete_form, 'formset': formset})
