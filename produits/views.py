from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, Count
from django.shortcuts import render, redirect, get_object_or_404

from core.pagination import paginer
from core.decorators import role_requis
from core.reponses import reponse_suppression
from .models import Categorie, Produit
from .forms import CategorieForm, ProduitForm


@login_required
def produit_liste(request):
    q = request.GET.get('q', '').strip()
    categorie_id = request.GET.get('categorie', '')
    statut = request.GET.get('statut', '')

    produits = Produit.objects.select_related('categorie').all()

    if q:
        produits = produits.filter(
            Q(reference__icontains=q) | Q(designation__icontains=q) | Q(code_barre__icontains=q)
        )
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    if statut == 'rupture':
        produits = produits.filter(quantite_stock__lte=0)
    elif statut == 'alerte':
        produits = produits.filter(quantite_stock__gt=0, quantite_stock__lte=F('seuil_alerte'))
    elif statut == 'actif':
        produits = produits.filter(est_actif=True)
    elif statut == 'inactif':
        produits = produits.filter(est_actif=False)

    page_obj = paginer(request, produits, 10)

    stats_globales = Produit.objects.aggregate(
        total=Count('id'),
        actifs=Count('id', filter=Q(est_actif=True)),
        valeur_stock=Sum(F('quantite_stock') * F('prix_achat')),
    )
    ruptures = Produit.objects.filter(quantite_stock__lte=0, est_actif=True).count()
    alertes = Produit.objects.filter(quantite_stock__gt=0, quantite_stock__lte=F('seuil_alerte'), est_actif=True).count()

    contexte = {
        'page_obj': page_obj,
        'q': q,
        'categories': Categorie.objects.filter(est_active=True),
        'categorie_id': categorie_id,
        'statut': statut,
        'stats': {
            'total': stats_globales['total'] or 0,
            'actifs': stats_globales['actifs'] or 0,
            'valeur_stock': stats_globales['valeur_stock'] or 0,
            'ruptures': ruptures,
            'alertes': alertes,
        },
    }
    template = 'produits/_produit_table.html' if request.htmx else 'produits/produit_liste.html'
    return render(request, template, contexte)


@login_required
def produit_detail(request, pk):
    produit = get_object_or_404(Produit.objects.select_related('categorie'), pk=pk)
    mouvements = produit.mouvements.all()[:15]
    return render(request, 'produits/produit_detail.html', {'produit': produit, 'mouvements': mouvements})


@login_required
def produit_creer(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save()
            messages.success(request, f"Le produit « {produit.designation} » a été créé avec succès.")
            return reponse_suppression(request, 'produits:produit_detail', pk=produit.pk)
        if request.htmx:
            return render(request, 'produits/_produit_modal.html', {'form': form, 'titre': 'Nouveau produit'})
    else:
        form = ProduitForm()
        if request.htmx:
            return render(request, 'produits/_produit_modal.html', {'form': form, 'titre': 'Nouveau produit'})
    return render(request, 'produits/produit_form.html', {'form': form, 'titre': 'Nouveau produit'})


@login_required
def produit_modifier(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit mis à jour avec succès.")
            return reponse_suppression(request, 'produits:produit_detail', pk=produit.pk)
        if request.htmx:
            return render(request, 'produits/_produit_modal.html', {'form': form, 'titre': 'Modifier le produit'})
    else:
        form = ProduitForm(instance=produit)
        if request.htmx:
            return render(request, 'produits/_produit_modal.html', {'form': form, 'titre': 'Modifier le produit'})
    return render(request, 'produits/produit_form.html', {'form': form, 'titre': 'Modifier le produit', 'produit': produit})


@login_required
@role_requis('peut_administrer', 'peut_gerer_stock')
def produit_supprimer(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.est_actif = False
        produit.save(update_fields=['est_actif'])
        messages.success(request, f"Le produit « {produit.designation} » a été désactivé (historique conservé).")
        return reponse_suppression(request, 'produits:produit_liste')
    return render(request, 'produits/_confirmer_suppression.html', {'objet': produit, 'url_annuler': 'produits:produit_detail'})


@login_required
@role_requis('peut_administrer', 'peut_gerer_stock')
def produit_reactiver(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.est_actif = True
        produit.save(update_fields=['est_actif'])
        messages.success(request, f"Le produit « {produit.designation} » a été réactivé.")
        return reponse_suppression(request, 'produits:produit_liste')
    return render(request, 'produits/_confirmer_reactivation.html', {'objet': produit})

# --- Catégories ---

@login_required
def categorie_liste(request):
    q = request.GET.get('q', '').strip()
    categories = Categorie.objects.all()
    if q:
        categories = categories.filter(libelle__icontains=q)
    page_obj = paginer(request, categories, 10)
    stats = {
        'total': Categorie.objects.count(),
        'actives': Categorie.objects.filter(est_active=True).count(),
    }
    template = 'produits/_categorie_table.html' if request.htmx else 'produits/categorie_liste.html'
    return render(request, template, {'page_obj': page_obj, 'q': q, 'stats': stats})


@login_required
def categorie_creer(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie créée avec succès.")
            return reponse_suppression(request, 'produits:categorie_liste')
        if request.htmx:
            return render(request, 'produits/_categorie_modal.html', {'form': form, 'titre': 'Nouvelle catégorie'})
    else:
        form = CategorieForm()
        if request.htmx:
            return render(request, 'produits/_categorie_modal.html', {'form': form, 'titre': 'Nouvelle catégorie'})
    return render(request, 'produits/categorie_form.html', {'form': form, 'titre': 'Nouvelle catégorie'})


@login_required
def categorie_modifier(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie mise à jour.")
            return reponse_suppression(request, 'produits:categorie_liste')
        if request.htmx:
            return render(request, 'produits/_categorie_modal.html', {'form': form, 'titre': 'Modifier la catégorie'})
    else:
        form = CategorieForm(instance=categorie)
        if request.htmx:
            return render(request, 'produits/_categorie_modal.html', {'form': form, 'titre': 'Modifier la catégorie'})
    return render(request, 'produits/categorie_form.html', {'form': form, 'titre': 'Modifier la catégorie'})


@login_required
@role_requis('peut_administrer')
def categorie_supprimer(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        categorie.est_active = False
        categorie.save(update_fields=['est_active'])
        messages.success(request, "Catégorie désactivée.")
        return reponse_suppression(request, 'produits:categorie_liste')
    return render(request, 'produits/_confirmer_suppression.html', {'objet': categorie, 'url_annuler': 'produits:categorie_liste'})
