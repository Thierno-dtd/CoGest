from django import template
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring_replace(context, **kwargs):
    """Reconstruit la query string en remplaçant/ajoutant des paramètres (utile pour la pagination + filtres)."""
    request = context['request']
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value
    return urlencode(params, doseq=True)


@register.filter
def fcfa(value):
    """Formate un nombre en devise FCFA avec séparateur de milliers : 1 250 000 FCFA"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    entier = int(round(value))
    formatte = f"{entier:,}".replace(',', ' ')
    return f"{formatte} FCFA"


@register.filter
def montant(value):
    """Formate un nombre avec séparateur de milliers, sans devise."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    entier = int(round(value))
    return f"{entier:,}".replace(',', ' ')


@register.filter
def pourcentage(value, decimales=1):
    try:
        return f"{float(value):.{int(decimales)}f}%"
    except (TypeError, ValueError):
        return value


@register.filter
def get_item(dictionnaire, cle):
    return dictionnaire.get(cle)
