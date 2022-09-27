from django.urls import path, re_path

from . import views

urlpatterns = [
    # path('', views.store, name='store'),
    
    # ProductListView
    path('', views.ProductListView.as_view(), name='store'),
    path('vendor/<slug:vendor_slug>/', views.ProductListView.as_view(), name='store_vendor'),
    re_path(r'^category/(?P<hierarchy>.+)/$', views.ProductListView.as_view(), name='products_by_category'),

    # ProductDetailView
    path('vendor/<slug:vendor_slug>/<slug:product_slug>/', views.ProductDetailView.as_view(), name='vendor_product_detail'),

    # path('category/<slug:category_slug>/', views.ProductListView.as_view(), name='products_by_category'),
    # path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    # path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>', views.submit_review, name='submit_review'),

    # Dashboard
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<slug:product_slug>/', views.edit_product, name='edit_product'),
    path('list_product/', views.list_product, name='list_product'),
    path('export/', views.export, name='export'),
    path('import_csv/', views.import_csv, name='import_csv'),

    # Variation Price
    path('variation/', views.variation_price, name='variation_price'),
    path('variation/<variation_id>/', views.variation_price, name='variation_price'),
]