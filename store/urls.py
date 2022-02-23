from django.urls import path

from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>', views.submit_review, name='submit_review'),

    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<slug:product_slug>/', views.edit_product, name='edit_product'),
    path('list_product/', views.list_product, name='list_product'),

    # Variation Price
    path('variation/', views.variation_price, name='variation_price'),
    path('variation/<variation_id>/', views.variation_price, name='variation_price'),
]