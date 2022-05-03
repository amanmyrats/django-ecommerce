from .models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)

def root_categories(request):
    roots = Category.objects.filter(parent=None)
    return dict(root_categories=roots)