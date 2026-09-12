from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('menu/', views.menu_view, name='menu'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
]
