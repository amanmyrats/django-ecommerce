from django.urls import path
from django.urls.resolvers import URLPattern
from . import views


urlpatterns = [
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activate_by_phone_number/', views.activate_by_phone_number, name='activate_by_phone_number'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword_validate_by_mobile/', views.resetpassword_validate_by_mobile, name='resetpassword_validate_by_mobile'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('update_phone_number/', views.update_phone_number, name='update_phone_number'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_vendor_id>/', views.order_detail, name='order_detail'),
    # path('order_detail_test/<int:order_vendor_id>/', views.order_detail_test, name='order_detail_test'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    # path('my_sales/', views.my_sales, name='my_sales'),
    # path('all_sales/', views.all_sales, name='all_sales'),

    path('all_sales/', views.SalesListView.as_view(), name='sales'),
    path('my_sales/<slug:vendor_slug>/', views.SalesListView.as_view(), name='vendor_sales'),
    path('my_sales/<slug:vendor_slug>/<slug:order_slug>/', views.SaleDetailView.as_view(), name='vendor_sale_detail'),
]