from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def home_view(request):
    bestsellers = Product.objects.filter(is_available=True, is_bestseller=True)[:8]
    popular_tea = Product.objects.filter(is_available=True, category__slug='tea')[:6]
    categories = Category.objects.all()
    return render(request, 'products/home.html', {
        'bestsellers': bestsellers,
        'popular_tea': popular_tea,
        'categories': categories,
    })


def menu_view(request):
    products = Product.objects.filter(is_available=True).select_related('category')

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    category_slug = request.GET.get('category', '').strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get('sort', '')
    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name': 'name',
        'newest': '-created_at',
    }
    products = products.order_by(sort_map.get(sort, '-is_bestseller'))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'products/menu.html', {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'query': query,
        'selected_category': category_slug,
        'sort': sort,
    })


def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:4]
    reviews = product.reviews.select_related('customer')[:10]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    })
