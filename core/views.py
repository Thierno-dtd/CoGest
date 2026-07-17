from django.shortcuts import render


def page_non_trouvee(request, exception=None):
    """Page 404 personnalisée — utilisée par handler404 (DEBUG=False) et par la route
    attrape-tout déclarée en dernier dans config/urls.py (visible même en DEBUG=True)."""
    return render(request, '404.html', status=404)


def erreur_serveur(request):
    """Page 500 personnalisée — utilisée uniquement quand DEBUG=False."""
    return render(request, '500.html', status=500)