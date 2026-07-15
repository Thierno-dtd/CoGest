from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/', views.profil, name='profil'),
    path('profil/modifier/', views.profil_modifier, name='profil_modifier'),
    path('profil/mot-de-passe/', views.mot_de_passe_modifier, name='mot_de_passe_modifier'),
]
