import csv
import imp
from random import randint
from pathlib import Path
from urllib import request

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
from django.core.files.storage import default_storage
from django.views.generic import ListView, DetailView

import django_filters

from ecommerce import settings
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
from .models import Color, Product, ProductGallery, ReviewRating, Variation, Size
from .forms import ReviewForm, ProductModelForm, VariationModelForm
from orders.models import OrderProduct
from accounts.models import Vendor
from .utils import get_vendor, export_model, import_model, add_variation_for_new_product

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
    vendor = get_object_or_404(Vendor, user = request.user)
    if request.method == 'POST':
        add_product_form = ProductModelForm(request.POST, request.FILES)
        add_product_form_without_image = ProductModelForm(request.POST)
        if add_product_form.is_valid():
            new_product = add_product_form_without_image.save(commit=False)
            new_product.owner = vendor
            new_product.image = add_product_form.cleaned_data['image']
            new_product.image_small = add_product_form.cleaned_data['image']
            new_product.image_thumbnail = add_product_form.cleaned_data['image']
            new_product.save()
            # Create version with no variation
            add_variation_for_new_product(new_product_id=new_product.pk)
            context['product'] = new_product
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


def export(request):
    # print(request.META)
    if request.method == 'POST':
        current_user = request.user
        model_name = request.GET.get('model_name')
        if not model_name:
            return redirect('list_product')
        vendor = get_object_or_404(Vendor, user=request.user)
        Path(settings.MEDIA_ROOT / 'Downloads' / str(current_user.pk)).mkdir(parents=True, exist_ok=True)
        download_path = Path(settings.MEDIA_ROOT) / 'Downloads' / str(current_user.pk)
        if model_name == 'product':
            with open(download_path / 'products.csv', 'w') as f:
                pass
            csv_file = download_path / 'products.csv'
            if current_user.is_staff:
                products = Product.objects.all()
            else:
                products = Product.objects.filter(owner=vendor)
            result = export_model(qs=products, model_name=model_name, csv_file=csv_file)
            if result:
                with open(csv_file, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="{}'.format('products.csv')
                    return response
        elif model_name == 'variation':
            with open(download_path / 'variations.csv', 'w') as f:
                pass
            csv_file = download_path / 'variations.csv'
            variations = Variation.objects.filter(product__owner=vendor)
            result = export_model(qs=variations, model_name=model_name, csv_file=csv_file)
            if result:
                with open(csv_file, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="{}'.format('variations.csv')
                    return response
        else:
            messages.error(request, _('This table cannot be exported'))
     
    return redirect('list_product')


def import_csv(request):
    if request.method == 'POST':
        current_user = request.user
        print('request is post')
        csv_file = request.FILES.get('csv_file')
        model_name = request.GET.get('model_name')
        print('csv_file', csv_file)
        if csv_file:
            Path(settings.MEDIA_ROOT / 'Uploads' / str(current_user.pk)).mkdir(parents=True, exist_ok=True)
            upload_path = Path(settings.MEDIA_ROOT) / 'Uploads' / str(current_user.pk)
            csv_file = default_storage.save(upload_path / csv_file.name, csv_file)
            print('csv_file', csv_file)
            result = import_model(request=request, csv_file=csv_file, model_name=model_name)
            print('result', result)
            if result:
                messages.success(request, _('Import was successfull.'))
            else:
                messages.error(request, _('Error occured when importing!'))
        else:
            messages.error(request, _('No Attachment!'))
    return redirect('list_product')



class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_everywhere', label='Search')
    # vendor = django_filters.CharFilter(field_name='owner', lookup_expr='in')
    # category  = django_filters.CharFilter(method='search_category', label='Category')
    color  = django_filters.CharFilter(field_name='productvariations__color', lookup_expr='in')
    size  = django_filters.CharFilter(field_name='productvariations__size', lookup_expr='in')
    # min_price  = django_filters.CharFilter(method='search_min_price', label='Min Price')
    # max_price  = django_filters.CharFilter(method='search_max_price', label='Max Price')

    class Meta:
        model = Product
        fields = ['search']
        # fields = ['search', 'vendor', 'category', 'color', 'size']
    
    def search_everywhere(self, queryset, name, value):
        return queryset.filter(Q(product_name__icontains=value) | Q(product_code__icontains=value) \
                | Q(brand__icontains=value) | Q(productvariations__sku__icontains=value) | Q(description__icontains=value))
    
    # def search_category(self, queryset, name, value):
    #     print('category value', value)
    #     category = get_object_or_404(Category, pk=value)
    #     if category.is_leaf_node():
    #         return queryset.filter(category=category, is_available=True)
    #     else:
    #         return queryset.filter(category__in=category.get_children(), is_available=True) 
    
    # def search_min_price(self, queryset, name, value):
    #     try:
    #         # return queryset.filter(Q(lowest_price__gte=int(value)) | Q(highest_price__gte=int(value)) )
    #         return queryset.filter(productvariations__sale_price__gte=int(value))
    #     except:
    #         return queryset
    
    # def search_max_price(self, queryset, name, value):
    #     try:
    #         # return queryset.filter(Q(highest_price__lte=int(value)) | Q(lowest_price__lte=int(value)))
    #         return queryset.filter(productvariations__sale_price__lte=int(value))
    #     except:
    #         return queryset


class ProductListView(ListView):
    model = Product
    template_name = 'store/store.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        self.vendors_page = False
        self.category_page = False
        self.category = None
        vendor_slug = self.kwargs.get('vendor_slug')
        # category_slug = self.kwargs.get('category_slug')
        hierarchy = self.kwargs.get('hierarchy')
        if hierarchy:
            category_slug = hierarchy.split('/')
        else:
            category_slug = None
        order = self.request.GET.get('order')

        self.current_parameters = dict(self.request.GET)
        print('self.current_parameters', self.current_parameters)
        incoming_parameters = {}
        self.current_url_parameter_except_page = ''
        for current_parameter in self.current_parameters:
            for v in self.current_parameters[current_parameter]:
                if not current_parameter=='page':
                    self.current_url_parameter_except_page += '{}={}&'.format(current_parameter, v)   
        products = Product.objects.filter(is_available=True)
        if vendor_slug:
            vendor = get_object_or_404(Vendor, slug=vendor_slug)
            products = Product.objects.filter(owner=vendor, is_available=True)
            self.vendors_page = True
        elif category_slug:
            parent = None 
            root = Category.objects.all()
            for slug in category_slug[:-1]:
                parent = root.get(parent=parent, slug=slug)

            self.category = get_object_or_404(Category, parent=parent, slug=category_slug[-1])
            products = products.filter(category__in=self.category.get_descendants(include_self=True), is_available=True)
            self.category_page = True
            

        # Price Range
        try:
            min_price = int(self.request.GET.get('min_price'))
            max_price = int(self.request.GET.get('max_price'))
            if max_price >= min_price:
                products = products.filter(productvariations__sale_price__gte=min_price, productvariations__sale_price__lte=max_price)
        except ValueError:
            pass
        except TypeError:
            pass
        
        # Category
        if self.current_parameters.get('category'):
            products_categories = Product.objects.none()
            for category_id in self.current_parameters.get('category'):
                try:
                    category_id = int(category_id)    
                    category = get_object_or_404(Category, pk=category_id)
                    temp_query = products.filter(category__in=category.get_descendants(include_self=True), is_available=True)
                    products_categories = products_categories | temp_query
                except ValueError:
                    pass
                except TypeError:
                    pass 
            products = products_categories.distinct()

        # django-filter FilterSet
        products = ProductFilter(self.request.GET, queryset=products).qs.distinct()
        print('self.request.GET', self.request.GET)
        # Ordering
        if order:
            if order == 'hightolow':
                products = products.order_by('-highest_price')
            elif order == 'lowtohigh':
                products = products.order_by('lowest_price')
            
        self.product_count = products.count()
        return products

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        nodes = Category.objects.all()
        testnode = nodes.first()
        context['product_count'] = self.product_count
        context['vendors_page'] = self.vendors_page
        context['category_page'] = self.category_page 
        context['current_parameters'] = self.current_parameters
        context['current_url_parameter_except_page'] = self.current_url_parameter_except_page
        context['nodes'] = nodes
        context['current_category'] = self.category
        return context


class ProductDetailView(DetailView):
    queryset = Product.objects.filter(is_available=True)
    template_name = 'store/product_detail.html'
    context_object_name = 'single_product'
    slug_url_kwarg = 'product_slug'
    
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        single_product = self.get_object()
        current_category = single_product.category
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(self.request), product=single_product).exists()

        if self.request.user.is_authenticated:
            try:
                orderproduct = OrderProduct.objects.filter(user=self.request.user, product_id=single_product.id).exists()
            except OrderProduct.DoesNotExist:
                orderproduct = None
        else:
            orderproduct = None

        # Get the reviews
        reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

        # Get the product gallery
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
        variation_gallery = Variation.objects.filter(product=single_product)

        context['in_cart'] = in_cart
        context['orderproduct'] = orderproduct
        context['reviews'] = reviews
        context['product_gallery'] = product_gallery
        context['variation_gallery'] = variation_gallery
        context['current_category'] = current_category
        
        return context
