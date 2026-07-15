from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import Utilisateur


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "Nom d'utilisateur", 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Mot de passe'}))


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email', 'telephone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'telephone': forms.TextInput(attrs={'class': 'input', 'placeholder': '+241 XX XX XX XX'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'input-file'}),
        }


class ChangerMotDePasseForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Mot de passe actuel'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Nouveau mot de passe'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Confirmer le nouveau mot de passe'}))
