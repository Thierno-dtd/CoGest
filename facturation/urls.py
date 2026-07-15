from django.urls import path
from . import views

app_name = 'facturation'

urlpatterns = [
    path('', views.facture_liste, name='facture_liste'),
    path('<int:pk>/', views.facture_detail, name='facture_detail'),
    path('<int:pk>/pdf/', views.facture_pdf, name='facture_pdf'),
]
