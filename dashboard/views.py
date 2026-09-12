from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import Order, OrderItem
from products.models import Category, Product
from .decorators import staff_required
from .forms import CategoryForm, ProductForm


@staff_required
def overview_view(request):
    today = timezone.now().date()

    total_orders = Order.objects.count()
    todays_orders = Order.objects.filter(created_at__date=today).count()
    total_customers = User.objects.filter(is_staff=False).count()
    total_products = Product.objects.count()
    total_sales = Order.objects.exclude(status=Order.Status.CANCELLED).aggregate(s=Sum('total'))['s'] or 0

    last_7_days = Order.objects.filter(created_at__date__gte=today - timezone.timedelta(days=6)) \
        .annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day')

    popular_products = OrderItem.objects.values('product_name') \
        .annotate(qty=Sum('quantity')).order_by('-qty')[:5]

    recent_orders = Order.objects.select_related('customer')[:8]

    return render(request, 'dashboard/overview.html', {
        'total_orders': total_orders,
        'todays_orders': todays_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'total_sales': total_sales,
        'last_7_days': list(last_7_days),
        'popular_products': list(popular_products),
        'recent_orders': recent_orders,
    })


@staff_required
def product_list_view(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'dashboard/product_list.html', {'products': products})


@staff_required
def product_form_view(request, product_id=None):
    product = get_object_or_404(Product, id=product_id) if product_id else None

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product {'updated' if product else 'created'} successfully.")
            return redirect('dashboard:products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product})


@staff_required
def product_delete_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect('dashboard:products')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


@staff_required
def category_list_view(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added.")
            return redirect('dashboard:categories')
    return render(request, 'dashboard/category_list.html', {'categories': categories, 'form': form})


@staff_required
def category_delete_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect('dashboard:categories')


@staff_required
def order_list_view(request):
    orders = Order.objects.select_related('customer').all()

    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)

    query = request.GET.get('q', '').strip()
    if query:
        orders = orders.filter(full_name__icontains=query)

    return render(request, 'dashboard/order_list.html', {
        'orders': orders, 'statuses': Order.Status.choices, 'status': status, 'query': query,
    })


@staff_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items').select_related('customer'), id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in Order.Status.values:
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
            return redirect('dashboard:order_detail', order_id=order.id)
    return render(request, 'dashboard/order_detail.html', {'order': order, 'statuses': Order.Status.choices})


@staff_required
def customer_list_view(request):
    customers = User.objects.filter(is_staff=False).select_related('profile').annotate(order_count=Count('orders'))
    return render(request, 'dashboard/customer_list.html', {'customers': customers})
