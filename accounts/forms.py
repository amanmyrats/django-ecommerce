import re

from django import forms
from django.utils.translation import gettext as _

from .models import Account, UserProfile

class RegistrationModelForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
    
    def __init__(self, *args, **kwargs):
        super(RegistrationModelForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['phone_number'].widget.attrs['type'] = 'tel'
        self.fields['phone_number'].widget.attrs['pattern'] = '6[1-5]{1}[1-9]{6}'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationModelForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError(
                _("Passwords do not match!")
            )
        elif not password:
            raise forms.ValidationError(
                _("Passwords cannot be empty!")
            )
        
        phone_number = cleaned_data.get('phone_number')
        if not re.match('^6[1-5]{1}[0-9]{6}$', phone_number):
            raise forms.ValidationError(
                _("Phone number is not valid Turkmenistan Tmcell number, must in format 6x xxxxxx")
            )

        
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid':_("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

