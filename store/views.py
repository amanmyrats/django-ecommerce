from random import randint

from django.core import paginator
from django.contrib import messages
from django.db.models.query_utils import Q
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template import context
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory

from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
from .models import Color, Product, ProductGallery, ReviewRating, Variation, Size
from .forms import ReviewForm, ProductModelForm, VariationModelForm
from orders.models import OrderProduct
from accounts.models import Vendor
from .utils import object_no_variation, get_vendor

def store(request, category_slug=None):
    categories = None
    products = None
     
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
    
    # Pagination
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products':paged_products,
        'product_count':product_count,
    }
    return render(request, 'store/store.html',context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e 

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    variation_gallery = Variation.objects.filter(product=single_product)

    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
        'variation_gallery': variation_gallery,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    
    context = {
        'products':products,
        'product_count':product_count,
    }
    return render(request, 'store/store.html', context )


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your revew has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
                

def variation_price(request):
    product_id = request.GET.get('product_id')
    color_id = request.GET.get('color_id')
    size_id = request.GET.get('size_id')

    context = {}

    if color_id == 'undefined':
        context['available_sizes'] = []
        nocolor = Color.objects.filter(name='No Variation')
        # print('nocolor', nocolor)
        if len(nocolor):
            color_id = nocolor[0].pk
            # print('color_id after ufndefined', color_id)
    else:
        variations = Variation.objects.filter(product_id=product_id, color_id=color_id)
        available_sizes=[]
        for variation in variations:
            if variation.in_stock:
                available_sizes.append(variation.size.id)
                context['available_sizes'] = available_sizes
    
    if size_id == 'undefined':
        nosize = Size.objects.filter(name='No Variation')
        # print('nosize', nosize)
        if len(nosize):
            size_id = nosize[0].pk
            # print('size_id after undefined', size_id)

    try:
        variation = Variation.objects.get(product_id=product_id, color_id=color_id, size_id=size_id)
        context['price'] = variation.sale_price
        context['variation_id'] = variation.id
    except Variation.DoesNotExist:
        pass
    return JsonResponse(context)

# Here check if user is in vendors group
# and logged in
def add_product(request):
    print('inside add_product')
    context = {}
    add_product_form = ProductModelForm()
    # try:
    vendor = get_object_or_404(Vendor, user = request.user)
    # except:
    #     # He is not a vendor
    #     return redirect('store')
    if request.method == 'POST':
        add_product_form = ProductModelForm(request.POST, request.FILES)
        add_product_form_without_image = ProductModelForm(request.POST)
        if add_product_form.is_valid():
            new_product = add_product_form_without_image.save(commit=False)
            new_product.owner = vendor 
            new_product.slug = slugify(str(new_product.product_name) + '-' + str(randint(1,1000000)) + '-' + str(vendor.id))
            new_product.save()
            new_product.image = add_product_form.cleaned_data['image']
            new_product.image_small = add_product_form.cleaned_data['image']
            new_product.image_thumbnail = add_product_form.cleaned_data['image']
            new_product.slug = slugify(str(new_product.product_name) + '-' + str(new_product.pk))
            print('new product slug in form', new_product.slug)
            new_product.save()
            print('this is new product', new_product)
            # Create version with no variation
            nocolor = object_no_variation(attr='Color')
            nosize = object_no_variation(attr='Size')
            print('color', nocolor, 'size', nosize)
            if nocolor and nosize:
                new_no_variation = Variation()
                new_no_variation.product = new_product
                new_no_variation.owner = vendor
                new_no_variation.color = nocolor 
                new_no_variation.size = nosize
                new_no_variation.quantity = 0
                new_no_variation.sale_price = 0
                new_no_variation.save()
                print('this is new variation', new_no_variation)
            context['product'] = new_product
            print('redirect to edit_product', redirect('edit_product', new_product.slug))
            return redirect('edit_product', new_product.slug)

    context['add_product_form'] = add_product_form
    return render(request, 'store/add_product.html', context)


def edit_product(request, product_slug=None):
    context = {}
    context['product_slug'] = product_slug
    if product_slug is None:
        return redirect('list_product')
    try:
        product = Product.objects.get(slug=product_slug)
    except:
        messages.error(request, _('There is no such product.'))
        return redirect('store')
    
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        messages.error(request, _('You are not a vendor.'))
        return redirect('store')
    # print('product', product)
    # print('vendor', vendor)
    product_form = ProductModelForm(instance=product)
    VariationInlineFormSet = inlineformset_factory(Product, Variation, fk_name='product', extra=0,
                            form=VariationModelForm)
    # variationformset = VariationInlineFormSet(instance=product, queryset=Variation.objects.filter(owner=vendor))
    variationformset = VariationInlineFormSet(instance=product)
    context['product_form'] = product_form
    context['variationformset'] = variationformset
    print('variationformset', variationformset)
    if request.method == 'POST':
        product_form = ProductModelForm(request.POST, request.FILES, instance=product)
        variationformset = VariationInlineFormSet(request.POST, request.FILES, instance=product)
        if product_form.is_valid() and variationformset.is_valid():
            new_product = product_form.save(commit=False)
            new_product.image_small = new_product.image
            new_product.image_thumbnail = new_product.image
            new_product.save()
            messages.success(request, _('Product was changed successfully.'))
            for form in variationformset:
                if form.is_valid():
                    new_variation = form.save(commit=False)
                    new_variation.owner = vendor
                    try:
                        new_variation.save()
                    except:
                        messages.error(request, _('Probably you already have this variation.'))
                        messages.error(request, _('Error when saving changes.'))
                        context['variationformset'] = variationformset
                        context['product_form'] = product_form
                        return render(request, 'store/edit_product.html', context)

            messages.success(request, _('Product variations were changed successfully.'))
            return redirect('list_product')
        else:
            variationformset = VariationInlineFormSet(request.POST, request.FILES,instance=product, 
                                queryset=Variation.objects.filter(owner=vendor))
            messages.error(request, _('Error when saving changes.'))
            context['variationformset'] = variationformset
            context['product_form'] = product_form
    
    return render(request, 'store/edit_product.html', context)


# Here check if user is in vendors group
# and logged in
def list_product(request):
    context = {}
    vendor = get_vendor(request=request)
    if not vendor:
        messages.error(request, _('You are not a vendor.'))
        return redirect('store')
    
    vendor_products = Product.objects.filter(owner=vendor).order_by('-created_date')
    # Add Paginator
    paginator = Paginator(vendor_products, 20)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    product_count = vendor_products.count()

    context['products'] = products
    context['product_count'] = product_count
    print('products',products)
    return render(request, 'store/list_product.html', context)