from django.urls import path
from django.urls.resolvers import URLPattern
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    # path('add_cart_variation/<int:product_id>/<int:variation_id>/', views.add_cart, name='add_cart_variation'),

    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),

    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),

    path('checkout/', views.checkout, name='checkout'),
]