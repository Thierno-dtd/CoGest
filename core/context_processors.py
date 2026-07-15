from django.conf import settings


def entreprise_info(request):
    return {
        'NOM_ENTREPRISE': getattr(settings, 'NOM_ENTREPRISE', 'Gestion Commerciale'),
        'DEVISE': getattr(settings, 'DEVISE', 'FCFA'),
    }
