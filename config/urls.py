from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from core.views import page_non_trouvee, erreur_serveur

handler404 = page_non_trouvee
handler500 = erreur_serveur

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('comptes/', include('accounts.urls')),
    path('produits/', include('produits.urls')),
    path('tiers/', include('tiers.urls')),
    path('stock/', include('stock.urls')),
    path('achats/', include('achats.urls')),
    path('ventes/', include('ventes.urls')),
    path('factures/', include('facturation.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^.*$', page_non_trouvee),
]
