from django import forms
from .models import Reglement


class ReglementForm(forms.ModelForm):
    class Meta:
        model = Reglement
        fields = ['date_paiement', 'montant_verse', 'mode_paiement', 'numero_transaction']
        widgets = {
            'date_paiement': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'montant_verse': forms.NumberInput(attrs={'class': 'input', 'step': '1'}),
            'mode_paiement': forms.Select(attrs={'class': 'input'}),
            'numero_transaction': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Optionnel'}),
        }
