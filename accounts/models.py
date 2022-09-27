import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext as _
from django_unique_slugify import unique_slugify
from django.urls import reverse

# from django_resized import ResizedImageField


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, phone_number, password=None):
        # if not email:
        #     raise ValueError('User must have an email address')
        
        if not phone_number:
            raise ValueError(_('User must have a phone number'))
        
        # if not username:
        #     raise ValueError('User must have an username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            phone_number=phone_number,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, email, username, phone_number, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
            phone_number=phone_number,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True 
        user.is_superadmin = True 
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    username       = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(max_length=100, unique=True)
    phone_number    = models.CharField(max_length=50, unique=True)

    # required
    date_joined     = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    is_superadmin   = models.BooleanField(default=False)
    is_vendor       = models.BooleanField(default=False)

    USERNAME_FIELD  = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'username']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class UserProfile(models.Model):
    def image_name(instance, filename):
        filename = '{}_profile.jpg'.format(instance.user.id)
        return os.path.join('userprofile', filename)
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    profile_picture = models.ImageField(blank=True, upload_to=image_name, default='photos/user/default.jpg')

    def __str__(self):
        return self.user.first_name

    def profile_picture_url(self):
        try:
            return self.profile_picture.url
        except:
            return None


class VerificationCode(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)

    def __str__(self):
        return str(self.code)


class BillingAddress(models.Model):
    user            = models.OneToOneField(Account, on_delete=models.CASCADE)
    phone_extra     = models.CharField(max_length=15, blank=True, null=True, default='')
    address_line_1  = models.CharField(max_length=50)
    address_line_2  = models.CharField(max_length=50, blank=True, null=True, default='')
    city            = models.CharField(max_length=50)
    state           = models.CharField(max_length=50, blank=True, null=True, default='')
    country         = models.CharField(max_length=50, blank=True, default='Turkmenistan')

    def full_address(self):
        return f'{self.address_line_1} / {self.address_line_2}'

    def __str__(self):
        return ('{} / {}'.format(str(self.address_line_1), str(self.city)))


class Vendor(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='vendors')
    official_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return str(self.official_name)
    
    def get_vendor_products_url(self):
        return reverse('store_vendor', args=[self.slug])

    def save(self, *args, **kwargs):
        # if self.official_name:
        #     self.slug = slugify(self.official_name)
        unique_slugify(self, str(self.official_name))
        super(Vendor, self).save(*args, **kwargs)


class Driver(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    car_brand = models.CharField(max_length=30)
    car_model = models.CharField(max_length=30)
    car_year = models.CharField(max_length=4)
    car_plate = models.CharField(max_length=15)
    mobile = models.CharField(max_length=30)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.first_name, self.last_name, self.car_model, self.car_plate, self.mobile)
    
    def save(self, *args, **kwargs):
        unique_slugify(self, str(self.first_name))
        super(Driver, self).save(*args, **kwargs)