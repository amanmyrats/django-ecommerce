from .models import Vendor


def vendors(request):
    vendors = Vendor.objects.all()
    logged_in_vendor = None
    if request.user.is_authenticated:
        logged_in_vendor = vendors.filter(user=request.user).first()
    return dict(vendors=vendors, logged_in_vendor=logged_in_vendor)