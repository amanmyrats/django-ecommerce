from random import randint, random
from attr import fields
import requests

from django.contrib import messages, auth
from django.contrib.auth.backends import RemoteUserBackend
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.translation import gettext as _
import django_filters

from .models import Account, UserProfile, Vendor, VerificationCode
from .forms import RegistrationModelForm, UserForm, UserProfileForm
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct, OrderDelivery
from orders.forms import OrderDeliveryModelForm, OrderPartialModelForm
from .utils import send_verification_sms
from carts.utils import order_vendor_info

def registration(request):
    if request.method == 'POST':
        # print('request is post')
        form = RegistrationModelForm(request.POST)
        if form.is_valid():
            # print('form is valid')
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = phone_number
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                phone_number=phone_number,
                password=password
            )
            user.save()
            # print('user created successfully', user)
            # Create instance of User in UserProfile model
            newly_registrated_user_profile = UserProfile()
            newly_registrated_user_profile.user = user
            newly_registrated_user_profile.save()
            # print('newly registered user registered into UserProfile model')

            # USER ACTIVATION with mail
                # current_site = get_current_site(request)
                # mail_subject = 'Please activate your account'
                # message = render_to_string('accounts/account_verification_email.html', {
                #     'user':user,
                #     'domain':current_site,
                #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                #     'token':default_token_generator.make_token(user),
                # })
                # to_email = email
                # send_email = EmailMessage(mail_subject, message, to=[to_email])
                # send_email.send()
                # messages.success(request, "We sent link to your mail, please click that link to activate your account.")
                # return redirect('/accounts/login/?command=mailverification&email='+email)

            # USER ACTIVATION with phone
            send_verification_sms(user=user)

            return redirect('/accounts/login/?command=mobileverification&mobile='+phone_number)
        else:
            # print('form is not valid')
            context = {'form':form}
            return render(request, 'accounts/registration.html', context)
    else:
        form = RegistrationModelForm()
    context = {
        'form':form,
    }
    
    return render(request, 'accounts/registration.html', context)


def update_phone_number(request):
    if request.method == 'POST':
        current_phone_number = request.POST.get('current_phone_number')
        updated_phone_number  = request.POST.get('updated_phone_number')
        possible_updated_user = Account.objects.filter(phone_number=updated_phone_number).exists()
        if possible_updated_user:
            messages.info(request, 'This number is already a member!')
            if request.user.is_authenticated:
                return redirect(reverse('edit_profile'))
            else:
                return redirect('login')
        if current_phone_number is not None:
            user = Account.objects.filter(phone_number=current_phone_number).exists()
            if not user:
                messages.info(request, 'There is no user with this phone number, please register first!')
                return redirect('registration')
            user = Account.objects.filter(phone_number=current_phone_number).first()
            # if request.user.phone_number:
            #     pass
            if user.is_active:
                if request.user.is_authenticated:
                    if not user.phone_number == request.user.phone_number:
                        messages.info(request, 'This user is already active!')
                        return redirect('login')
                else:
                    messages.info(request, 'This user is already active, if that is you, please login!')
                    return redirect('login')
            # print('user', user)
            if user is not None:
                user.phone_number = updated_phone_number
                user.is_active = False
                user.save()

                # Send SMS
                send_verification_sms(user=user)

                if request.user.is_authenticated:
                    logout(request)
                return redirect('/accounts/login/?command=mobileverification&mobile='+updated_phone_number)
    current_phone_number_from_get_request = request.GET.get('current_phone_number')
    if current_phone_number_from_get_request is not None:
        return render(request, 'accounts/update_phone_number.html')
    else:
        return redirect('login')


def login(request):
    if request.method == 'POST':
        # email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        # user = auth.authenticate(request, email=email, password=password)
        user = auth.authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_has_item = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_has_item:
                    variation_ids_to_add = []
                    cart_items_to_add_to_user = CartItem.objects.filter(cart=cart)
                    for item in cart_items_to_add_to_user:
                        variation_ids_to_add.append(item.variation.id)

                    # Get the cart items from the user to access his product variations
                    users_existing_cart_items = CartItem.objects.filter(user=user)
                    variation_ids_user_had = []
                    for item in users_existing_cart_items:
                        variation_ids_user_had.append(item.variation.id)
                    
                    for variation_id in variation_ids_to_add:
                        item_to_add = CartItem.objects.get(cart=cart, variation_id=variation_id)
                        if variation_id in variation_ids_user_had:
                            item_to_be_updated = CartItem.objects.get(user=user, variation_id=variation_id)
                            item_to_be_updated.quantity += item_to_add.quantity
                            item_to_be_updated.save()
                        else:
                            new_item_for_user = CartItem()
                            new_item_for_user.user = user
                            new_item_for_user.product = item_to_add.product
                            new_item_for_user.variation = item_to_add.variation
                            new_item_for_user.quantity = item_to_add.quantity
                            new_item_for_user.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            possible_user = Account.objects.filter(phone_number=phone_number).first()
            if possible_user is not None:
                if not possible_user.is_active:
                    return redirect('/accounts/login/?command=mobileverification&mobile='+phone_number)
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html', {})


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    # ACTIVATE USER BY MAIL
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('registration')


def activate_by_phone_number(request):
    # ACTIVATE USER BY PHONE NUMBER
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        mobile_verification_code = request.POST.get('mobile_verification_code')
        # print('phone_number', phone_number)
        # print('mobile_verification_code', mobile_verification_code)
        try:
            # user = Account.objects.get(phone_number=phone_number)
            user = get_object_or_404(Account, phone_number=phone_number)
            # print('user', user)
            try:
                true_verification_code = user.verificationcode.code
            except:
                true_verification_code = None
            # print('true_verification_code', true_verification_code)
            if true_verification_code:
                if mobile_verification_code==true_verification_code:
                    user.is_active=True 
                    user.save()
                    verified_user = VerificationCode.objects.filter(user=user)
                    for vu in verified_user:
                        vu.delete()
                    messages.success(request, 'Your account was activated successfully! You can login now.')
                    return redirect('login')
                else:
                    print('verification code is not same')
                    messages.error(request, 'Invalid Activation Code')
                    return redirect('registration')
            else:
                print('Interesting, there is no verification code assigned to this user.')
                messages.error(request, 'Interesting, there is no verification code assigned to this user.')
                return redirect('registration')
        except:
            # print('no user found')
            messages.error(request, 'We do not have a user with this number. Please write your phone in correct format, without 993')
            return redirect('registration')


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    try:
        userprofile = UserProfile.objects.get(user_id=request.user.id)
    except:
        userprofile = UserProfile.objects.create(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    # verificationcode=request.GET.get('verificationcode')
    # enternewpassword=request.GET.get('enternewpassword')
    if request.method == 'POST':
        # email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        if Account.objects.filter(phone_number__exact=phone_number).exists():
            # user = Account.objects.get(phone_number=phone_number)
            user = get_object_or_404(Account, phone_number=phone_number)

            # FORGOT PASSWORD WITH PHONE NUMBER
            send_verification_sms(user=user)

            messages.success(request, 'We have sent a code to reset your password, write code here to reset your password.')
            context = {
                'phone_number':phone_number,
            }
            return render(request, 'accounts/forgotPassword.html', context)
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgotPassword')
        

    
    context = {}
    messages.info(request, _('Write your phone number to reset your password. If your phone number is registered in our system, we will send you verification code.'))
    return render(request, 'accounts/forgotPassword.html', context)


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please choose new password.')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetpassword_validate_by_mobile(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        verification_code = request.POST.get('verification_code')
        user_exists = Account.objects.filter(phone_number=phone_number).exists()
        if not user_exists:
            messages.error(request, _('This user does not exist'))
            return redirect('login')
        user = Account.objects.filter(phone_number=phone_number).first()
        verificationcode_from_database_exists = VerificationCode.objects.filter(user=user).exists()
        if not verificationcode_from_database_exists:
            messages.error(request, _('We did not send you any verification code.'))
            return redirect('login')
        verificationcode_from_database = VerificationCode.objects.filter(user=user).first()
        try:
            check_old_verification = VerificationCode.objects.filter(user=user)
            for u in check_old_verification:
                u.delete()
        except:
            pass
        if str(verificationcode_from_database) == str(verification_code):
            messages.success(request, _('Please choose new password.'))
            context = {
                'phone_number':phone_number,
            }
            return render(request, 'accounts/resetPassword.html', context)
        else:
            messages.error(request, _('This code is not matching!'))
            return redirect('login')
            
    else:
        return redirect('resetPassword')
        

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone_number = request.POST.get('phone_number')
        # print(password)
        # print(confirm_password)
        # print(phone_number)
        
        if password == confirm_password:
            # uid = request.session.get('uid')
            user = get_object_or_404(Account, phone_number=phone_number)
            # print('user', user)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            context = {
                'phone_number':phone_number,
            }
            return render(request, 'accounts/resetPassword.html', context)
    else:
        context = {}
        return render(request, 'accounts/resetPassword.html', context)


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except:
        userprofile = UserProfile()
        userprofile.user = request.user
        userprofile.save()
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Something went wrong, update failed.')
            return redirect('edit_profile')
    
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = get_object_or_404(Account, phone_number__exact=request.user.phone_number)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Please enter valid current password!')
        else:
            messages.error(request, 'Password does not match!')
        return redirect('change_password')
    context = {}
    return render(request, 'accounts/change_password.html', context)

@login_required(login_url='login')
def order_detail(request, order_vendor_id):
    # superuserseeall = request.GET.get('superuserseeall')
    current_user = request.user

    order = get_object_or_404(Order, order_number_vendor=order_vendor_id)
    if order.user==current_user or current_user.is_staff:
        context = {
            'order': order,
        }
        return render(request, 'accounts/order_detail.html', context)
    else:
        return redirect('store')


# @login_required(login_url='login')
# def my_sales(request):
#     context = {}
#     status = request.GET.get('status')
#     edit = request.GET.get('edit')

#     if edit:
#         sale_id = edit
#         sale = get_object_or_404(OrderDelivery, id=sale_id)
#         context['sale'] = sale
#         form = OrderDeliveryModelForm(instance=sale)
#         context['form'] = form
#         if request.method == 'POST':
#             updated_sale_form = OrderDeliveryModelForm(request.POST, instance=sale)
#             context['form'] = updated_sale_form
#             if updated_sale_form.is_valid():
#                 updated_sale_form.save()
#                 return redirect('my_sales')
#             else:
#                 print('form is not valid')
#         return render(request, 'accounts/my_sales.html', context)
#     vendor = get_object_or_404(Vendor, user=request.user)
#     sales_all = OrderDelivery.objects.filter(vendor=vendor).order_by('-created_at')

#     if status:
#         sales_all = sales_all.filter(status=status)

#     # Pagination
#     paginator = Paginator(sales_all, 50)
#     page = request.GET.get('page')
#     sales = paginator.get_page(page)
#     sales_count = sales_all.count()

#     context['sales'] = sales
#     context['sales_count'] = sales_count
#     return render(request, 'accounts/my_sales.html', context)

# @login_required(login_url='login')
# def all_sales(request):
#     if not request.user.is_staff:
#         return redirect('dashboard')
#     context = {}
#     status = request.GET.get('status')
#     sales_all = OrderDelivery.objects.all()

#     if status:
#         sales_all = sales_all.filter(status=status).order_by('-created_at')

#     # Pagination
#     paginator = Paginator(sales_all, 50)
#     page = request.GET.get('page')
#     sales = paginator.get_page(page)
#     sales_count = sales_all.count()

#     context['sales'] = sales
#     context['sales_count'] = sales_count
#     return render(request, 'accounts/all_sales.html', context)

class SalesFilterSet(django_filters.FilterSet):
    class Meta:
        model = Order 
        fields = ['status']


class SalesListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'accounts/sales.html'
    context_object_name = 'sales'
    paginate_by = 10
    login_url = '/accounts/login/'

    def get_queryset(self):
        vendor_slug = self.kwargs.get('vendor_slug')
        print('vendor slug', vendor_slug)
        sales = Order.objects.all()
        if vendor_slug:
            sales = sales.filter(vendor__slug=vendor_slug)
        if self.request.GET.get('status'):
            sales = SalesFilterSet(self.request.GET, queryset=sales).qs.distinct()
        return sales

    def get_context_data(self, **kwargs):
        context = super(SalesListView, self).get_context_data(**kwargs)
        return context


class SaleDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Order
    template_name = 'accounts/order_detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'order_slug'     
    form_class = OrderPartialModelForm

    def get_success_url(self):
        try:
            vendor = Vendor.objects.get(user=self.request.user)
            return reverse('vendor_sales', kwargs={'vendor_slug':vendor.slug})
        except Vendor.DoesNotExist:
            return reverse('sales')
        # if self.request.user.is_vendor:
        # else:
        #     return reverse('sales')
    
    def get_context_data(self, **kwargs):
        context = super(SaleDetailView, self).get_context_data(**kwargs)
        form = OrderPartialModelForm(instance=self.get_object())
        context['form'] = form
        return context
    
    def post(self, request, *args, **kwargs):
        form = OrderPartialModelForm(request.POST, instance=self.get_object())
        if form.is_valid():
            return self.form_valid(form)
        else:
            return render(request, self.template_name, {'errors': form.errors, 'form':form})
    
    def form_valid(self, form):
        form.save()
        return super(SaleDetailView, self).form_valid(form)
