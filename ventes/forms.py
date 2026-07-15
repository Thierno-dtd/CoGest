from django import forms
from django.forms import formset_factory
from produits.models import Produit
from tiers.models import Client


class VenteEnteteForm(forms.Form):
    client = forms.ModelChoiceField(
        queryset=Client.objects.filter(est_actif=True),
        widget=forms.Select(attrs={'class': 'input'})
    )
    date_vente = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'})
    )


class LigneVenteForm(forms.Form):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.filter(est_actif=True),
        widget=forms.Select(attrs={'class': 'input ligne-produit'})
    )
    quantite = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'input ligne-qte'}))
    prix_vente_unitaire = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'input ligne-prix', 'placeholder': 'Prix catalogue par défaut'})
    )
    remise_pourcentage = forms.DecimalField(
        required=False, min_value=0, max_value=100, initial=0,
        widget=forms.NumberInput(attrs={'class': 'input ligne-remise'})
    )


LigneVenteFormSet = formset_factory(LigneVenteForm, extra=1, can_delete=True)
