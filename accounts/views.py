from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render

from orders.models import Order
from .forms import LoginForm, ProfileForm, RegisterForm
from .models import CustomerProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                data = form.cleaned_data
                username = data['email']
                user = User.objects.create_user(
                    username=username,
                    email=data['email'],
                    password=data['password'],
                )
                name_parts = data['name'].strip().split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                user.save()
                CustomerProfile.objects.create(user=user, phone=data['phone'])
            login(request, user)
            messages.success(request, f"Welcome to Chaay House, {user.first_name}!")
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Allow login with either username or email
            user_obj = User.objects.filter(email=identifier).first()
            username = user_obj.username if user_obj else identifier
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next') or 'home'
                return redirect(next_url)
            messages.error(request, "Invalid email/username or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def profile_view(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = ProfileForm(
            instance=profile,
            initial={'first_name': request.user.first_name, 'email': request.user.email},
        )

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    order = Order.objects.filter(customer=request.user, id=order_id).prefetch_related('items').first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect('accounts:my_orders')
    return render(request, 'accounts/order_detail.html', {'order': order})
