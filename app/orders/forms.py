from django import forms

from .models import Order, OrderDelivery


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order 
        fields = ['first_name', 'last_name', 'phone', 'phone_extra', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']


class OrderDeliveryModelForm(forms.ModelForm):
    class Meta:
        model = OrderDelivery
        fields = ['order', 'vendor', 'status', 'driver', 'delivery_fee']
        readonly_fields = ['vendor', 'order']

    def __init__(self, *args, **kwargs):
        super(OrderDeliveryModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['order'].widget.attrs['readonly'] = True
        self.fields['vendor'].widget.attrs['readonly'] = True


class OrderPartialModelForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_number_vendor', 'status', 'driver', 'driver_fee']
        readonly_fields = ['order_number_vendor']

    def __init__(self, *args, **kwargs):
        super(OrderPartialModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        # self.fields['vendor'].widget.attrs['readonly'] = True
        self.fields['order_number_vendor'].widget.attrs['readonly'] = True
        