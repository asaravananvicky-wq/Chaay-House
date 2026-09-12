from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview_view, name='overview'),
    path('products/', views.product_list_view, name='products'),
    path('products/add/', views.product_form_view, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_form_view, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete_view, name='product_delete'),
    path('categories/', views.category_list_view, name='categories'),
    path('categories/<int:category_id>/delete/', views.category_delete_view, name='category_delete'),
    path('orders/', views.order_list_view, name='orders'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('customers/', views.customer_list_view, name='customers'),
]
