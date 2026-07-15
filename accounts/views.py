from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

from .forms import ConnexionForm, ProfilForm, ChangerMotDePasseForm


class ConnexionView(LoginView):
    template_name = 'accounts/connexion.html'
    authentication_form = ConnexionForm
    redirect_authenticated_user = True


@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('accounts:connexion')


@login_required
def profil(request):
    return render(request, 'accounts/profil.html')


@login_required
def profil_modifier(request):
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('accounts:profil')
    else:
        form = ProfilForm(instance=request.user)
    return render(request, 'accounts/profil_form.html', {'form': form})


@login_required
def mot_de_passe_modifier(request):
    if request.method == 'POST':
        form = ChangerMotDePasseForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été modifié avec succès.")
            return redirect('accounts:profil')
    else:
        form = ChangerMotDePasseForm(request.user)
    return render(request, 'accounts/mot_de_passe_form.html', {'form': form})
