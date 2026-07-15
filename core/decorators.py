from functools import wraps
from django.core.exceptions import PermissionDenied


def role_requis(*roles_ou_test):
    """
    Décorateur pour restreindre une vue à certains rôles.
    Usage: @role_requis('peut_administrer') ou @role_requis(lambda u: u.is_staff)
    """
    def decorateur(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            for test in roles_ou_test:
                if callable(test):
                    if test(user):
                        return view_func(request, *args, **kwargs)
                elif hasattr(user, test) and getattr(user, test)():
                    return view_func(request, *args, **kwargs)
            raise PermissionDenied("Vous n'avez pas les droits nécessaires pour cette action.")
        return wrapper
    return decorateur
