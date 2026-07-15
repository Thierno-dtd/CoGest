from django.utils import timezone


def generer_numero(prefixe, model, champ='numero'):
    """
    Génère un numéro séquentiel du type PREFIXE-ANNEE-0001.
    """
    annee = timezone.localdate().year
    debut = f"{prefixe}-{annee}-"
    dernier = model.objects.filter(**{f"{champ}__startswith": debut}).order_by(f'-{champ}').first()
    if dernier:
        dernier_num = getattr(dernier, champ)
        try:
            seq = int(dernier_num.split('-')[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{debut}{seq:04d}"
