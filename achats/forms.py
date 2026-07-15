from django import forms
from django.forms import formset_factory
from produits.models import Produit
from tiers.models import Fournisseur
from .models import Achat


class AchatEnteteForm(forms.Form):
    fournisseur = forms.ModelChoiceField(
        queryset=Fournisseur.objects.filter(est_actif=True),
        widget=forms.Select(attrs={'class': 'input'})
    )
    date_achat = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'})
    )
    date_livraison_prevue = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'})
    )
    statut_livraison = forms.ChoiceField(
        choices=Achat.StatutLivraison.choices,
        initial=Achat.StatutLivraison.RECUE,
        widget=forms.Select(attrs={'class': 'input'})
    )
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'input', 'rows': 2}))


class LigneAchatForm(forms.Form):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.filter(est_actif=True),
        widget=forms.Select(attrs={'class': 'input ligne-produit'})
    )
    quantite = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'input ligne-qte'}))
    prix_achat_unitaire = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'input ligne-prix', 'placeholder': 'Prix catalogue par défaut'})
    )

    def clean(self):
        cleaned = super().clean()
        return cleaned


LigneAchatFormSet = formset_factory(LigneAchatForm, extra=1, can_delete=True)
