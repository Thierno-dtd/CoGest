from django import forms
from .models import Client, Fournisseur


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['type_client', 'nom', 'prenom', 'telephone', 'email', 'adresse', 'plafond_credit', 'est_actif']
        widgets = {
            'type_client': forms.Select(attrs={'class': 'input', 'x-model': 'typeClient'}),
            'nom': forms.TextInput(attrs={'class': 'input'}),
            'prenom': forms.TextInput(attrs={'class': 'input'}),
            'telephone': forms.TextInput(attrs={'class': 'input', 'placeholder': '+241 XX XX XX XX'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'adresse': forms.TextInput(attrs={'class': 'input'}),
            'plafond_credit': forms.NumberInput(attrs={'class': 'input'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'switch-input'}),
        }


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['raison_sociale', 'telephone', 'email', 'adresse', 'contact_principal',
                  'delai_livraison_moyen_jours', 'est_actif']
        widgets = {
            'raison_sociale': forms.TextInput(attrs={'class': 'input'}),
            'telephone': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'adresse': forms.TextInput(attrs={'class': 'input'}),
            'contact_principal': forms.TextInput(attrs={'class': 'input'}),
            'delai_livraison_moyen_jours': forms.NumberInput(attrs={'class': 'input'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'switch-input'}),
        }
