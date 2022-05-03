from .models import Color, Size


def all_colors(request):
    all_colors = Color.objects.all()
    return dict(all_colors=all_colors)

def all_sizes(request):
    all_sizes = Size.objects.all()
    return dict(all_sizes=all_sizes)