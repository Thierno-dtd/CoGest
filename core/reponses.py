from django.http import HttpResponse
from django.shortcuts import redirect


def reponse_suppression(request, redirect_view_name, **kwargs):
    """Réponse uniforme après une action de suppression/désactivation :
    - si la requête vient de HTMX (modale), on déclenche un rafraîchissement complet de page
    - sinon, redirection classique
    """
    if getattr(request, 'htmx', False):
        resp = HttpResponse(status=204)
        resp['HX-Refresh'] = 'true'
        return resp
    return redirect(redirect_view_name, **kwargs)
