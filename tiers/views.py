from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from core.pagination import paginer
from core.decorators import role_requis
from core.reponses import reponse_suppression
from .models import Client, Fournisseur
from .forms import ClientForm, FournisseurForm


@login_required
def client_liste(request):
    q = request.GET.get('q', '').strip()
    type_client = request.GET.get('type', '')

    clients = Client.objects.all()
    if q:
        clients = clients.filter(Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(telephone__icontains=q) | Q(email__icontains=q))
    if type_client:
        clients = clients.filter(type_client=type_client)

    page_obj = paginer(request, clients, 10)

    il_y_a_30j = timezone.localdate() - timedelta(days=30)
    stats = {
        'total': Client.objects.count(),
        'actifs': Client.objects.filter(est_actif=True).count(),
        'nouveaux_30j': Client.objects.filter(date_inscription__gte=il_y_a_30j).count(),
        'entreprises': Client.objects.filter(type_client=Client.TypeClient.ENTREPRISE).count(),
    }
    template = 'tiers/_client_table.html' if request.htmx else 'tiers/client_liste.html'
    return render(request, template, {'page_obj': page_obj, 'q': q, 'type_client': type_client, 'stats': stats})


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    ventes = client.ventes.all()[:10]
    return render(request, 'tiers/client_detail.html', {'client': client, 'ventes': ventes})


@login_required
def client_creer(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"Client « {client.nom_complet} » créé avec succès.")
            return redirect('tiers:client_detail', pk=client.pk)
    else:
        form = ClientForm()
    return render(request, 'tiers/client_form.html', {'form': form, 'titre': 'Nouveau client'})


@login_required
def client_modifier(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client mis à jour avec succès.")
            return redirect('tiers:client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    return render(request, 'tiers/client_form.html', {'form': form, 'titre': 'Modifier le client', 'client': client})


@login_required
@role_requis('peut_administrer', 'peut_vendre')
def client_supprimer(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.est_actif = False
        client.save(update_fields=['est_actif'])
        messages.success(request, f"Client « {client.nom_complet} » désactivé (historique conservé).")
        return reponse_suppression(request, 'tiers:client_liste')
    return render(request, 'tiers/_confirmer_suppression.html', {'objet': client, 'url_annuler': 'tiers:client_detail'})


# --- Fournisseurs ---

@login_required
def fournisseur_liste(request):
    q = request.GET.get('q', '').strip()
    fournisseurs = Fournisseur.objects.all()
    if q:
        fournisseurs = fournisseurs.filter(Q(raison_sociale__icontains=q) | Q(telephone__icontains=q) | Q(email__icontains=q))

    page_obj = paginer(request, fournisseurs, 10)
    stats = {
        'total': Fournisseur.objects.count(),
        'actifs': Fournisseur.objects.filter(est_actif=True).count(),
        'delai_moyen': Fournisseur.objects.aggregate(m=Sum('delai_livraison_moyen_jours'))['m'] or 0,
    }
    if stats['total']:
        stats['delai_moyen'] = round(stats['delai_moyen'] / stats['total'], 1)
    template = 'tiers/_fournisseur_table.html' if request.htmx else 'tiers/fournisseur_liste.html'
    return render(request, template, {'page_obj': page_obj, 'q': q, 'stats': stats})


@login_required
def fournisseur_detail(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    achats = fournisseur.achats.all()[:10]
    return render(request, 'tiers/fournisseur_detail.html', {'fournisseur': fournisseur, 'achats': achats})


@login_required
def fournisseur_creer(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f"Fournisseur « {fournisseur.raison_sociale} » créé avec succès.")
            return redirect('tiers:fournisseur_detail', pk=fournisseur.pk)
    else:
        form = FournisseurForm()
    return render(request, 'tiers/fournisseur_form.html', {'form': form, 'titre': 'Nouveau fournisseur'})


@login_required
def fournisseur_modifier(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur mis à jour avec succès.")
            return redirect('tiers:fournisseur_detail', pk=fournisseur.pk)
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'tiers/fournisseur_form.html', {'form': form, 'titre': 'Modifier le fournisseur', 'fournisseur': fournisseur})


@login_required
@role_requis('peut_administrer')
def fournisseur_supprimer(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.est_actif = False
        fournisseur.save(update_fields=['est_actif'])
        messages.success(request, f"Fournisseur « {fournisseur.raison_sociale} » désactivé.")
        return reponse_suppression(request, 'tiers:fournisseur_liste')
    return render(request, 'tiers/_confirmer_suppression.html', {'objet': fournisseur, 'url_annuler': 'tiers:fournisseur_detail'})
