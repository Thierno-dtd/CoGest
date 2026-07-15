from django import forms
from .models import Categorie, Produit


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['libelle', 'description', 'est_active']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ex : Électronique'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3, 'placeholder': 'Description (optionnel)'}),
            'est_active': forms.CheckboxInput(attrs={'class': 'switch-input'}),
        }


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['reference', 'designation', 'categorie', 'prix_achat', 'prix_vente',
                  'quantite_stock', 'seuil_alerte', 'taux_tva', 'unite_mesure',
                  'code_barre', 'image', 'est_actif']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ex : PRD-0001'}),
            'designation': forms.TextInput(attrs={'class': 'input', 'placeholder': "Nom de l'article"}),
            'categorie': forms.Select(attrs={'class': 'input'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'input', 'step': '1'}),
            'prix_vente': forms.NumberInput(attrs={'class': 'input', 'step': '1'}),
            'quantite_stock': forms.NumberInput(attrs={'class': 'input'}),
            'seuil_alerte': forms.NumberInput(attrs={'class': 'input'}),
            'taux_tva': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
            'unite_mesure': forms.Select(attrs={'class': 'input'}),
            'code_barre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Optionnel'}),
            'image': forms.ClearableFileInput(attrs={'class': 'input-file'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'switch-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # On ne permet plus la modification manuelle du stock une fois le produit créé :
            # il ne doit évoluer que via les achats/ventes.
            self.fields['quantite_stock'].disabled = True
            self.fields['quantite_stock'].help_text = "Le stock ne se modifie que via un achat ou une vente."
