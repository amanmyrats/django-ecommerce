from django import forms
from django.utils.translation import gettext as _
from .models import Product, ReviewRating, Variation


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']


class ProductModelForm(forms.ModelForm):
    image = forms.ImageField(required=False, error_messages={'invalid':(_("Image files only"))}, widget=forms.FileInput)
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'image', 'category']

    def __init__(self, *args, **kwargs):
        super(ProductModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class VariationModelForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ('color', 'size', 'quantity', 'items_in_package', 'currency', 'initial_price', 'expense_percentage', 'expense_fixed')
    
    def __init__(self, *args, **kwargs):
        super(VariationModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'