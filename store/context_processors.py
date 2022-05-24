from django.conf import settings

from .models import Color, Size


def all_colors(request):
    all_colors = Color.objects.all()
    return dict(all_colors=all_colors)

def all_sizes(request):
    all_sizes = Size.objects.all()
    return dict(all_sizes=all_sizes)

def wholesale_check(request):
    print('wholesale', settings.WHOLESALE)
    if settings.WHOLESALE:
        return {'is_wholesale':True}
    else:
        return {'is_wholesale':False}