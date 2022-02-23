from store.models import Color, Size
from accounts.models import Vendor

def object_no_variation(attr=None):
    if attr is None:
        return False 

    if attr == 'Color':
        try:
            nocolor = Color.objects.get(name='No Variation')
            return nocolor
        except:
            return False

    if attr == 'Size':
        try:
            nosize = Size.objects.get(name='No Variation')
            return nosize
        except:
            return False

def get_vendor(request=None):
    if request is None:
        return False 

    try:
        vendor = Vendor.objects.get(user=request.user)
        return vendor
    except:
        return False
