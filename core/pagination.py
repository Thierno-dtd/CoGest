from django.core.paginator import Paginator


def paginer(request, queryset, par_page=10):
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, par_page)
    page_obj = paginator.get_page(page_number)
    return page_obj
