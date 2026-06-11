from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import *
import json


def home(request):
    featured = Product.objects.filter(is_featured=True, is_active=True)[:6]
    categories = Category.objects.all()[:6]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    return render(request, 'store/home.html', {
        'featured': featured, 'categories': categories, 'new_arrivals': new_arrivals
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    query = request.GET.get('q', '')
    category = request.GET.get('cat', '')
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')
    sort = request.GET.get('sort', '')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        products = products.filter(category__slug=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products, 'categories': categories, 'query': query,
        'selected_cat': category, 'sort': sort
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    reviews = product.reviews.all().select_related('user')
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.update_or_create(
            product=product, user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, 'Review submitted!')
        return redirect('product_detail', slug=slug)
    return render(request, 'store/product_detail.html', {
        'product': product, 'related': related, 'reviews': reviews, 'in_wishlist': in_wishlist
    })


# ===== CART =====
@login_required
def cart(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    items = cart_obj.items.select_related('product').all()
    return render(request, 'store/cart.html', {'cart': cart_obj, 'items': items})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if product.stock <= 0:
        messages.error(request, 'Product out of stock!')
        return redirect('product_detail', slug=product.slug)
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product)
    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
            messages.success(request, f'Updated {product.name} quantity in cart.')
        else:
            messages.warning(request, 'Maximum stock reached.')
    else:
        messages.success(request, f'{product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    action = request.POST.get('action')
    if action == 'increase' and item.quantity < item.product.stock:
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    elif action == 'remove':
        item.delete()
    return redirect('cart')


@login_required
def checkout(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    items = cart_obj.items.select_related('product').all()
    if not items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')

    coupon_discount = 0
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            coupon_discount = int(cart_obj.get_total() * coupon.discount_percent / 100)
        except:
            pass

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method', 'cod')
        notes = request.POST.get('notes', '')
        total = cart_obj.get_total() - coupon_discount

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            shipping_address=address,
            phone=phone,
            payment_method=payment_method,
            notes=notes,
            payment_status='paid' if payment_method != 'cod' else 'pending'
        )
        for item in items:
            OrderItem.objects.create(
                order=order, product=item.product,
                product_name=item.product.name,
                price=item.product.price, quantity=item.quantity
            )
            item.product.stock -= item.quantity
            item.product.save()
        cart_obj.items.all().delete()
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
        messages.success(request, f'Order #{order.order_number} placed successfully!')
        if payment_method != 'cod':
            return redirect('razorpay_payment', order.pk)
        return redirect('order_success', order.pk)

    return render(request, 'store/checkout.html', {
        'cart': cart_obj, 'items': items, 'coupon_discount': coupon_discount
    })


@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').upper()
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            cart_obj = request.user.cart
            if cart_obj.get_total() >= coupon.minimum_amount:
                request.session['coupon_code'] = code
                messages.success(request, f'Coupon applied! {coupon.discount_percent}% off.')
            else:
                messages.error(request, f'Minimum order amount ₹{coupon.minimum_amount} required.')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    return redirect('checkout')


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': user_orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


# Wishlist
@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'items': items})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        messages.info(request, f'Removed from wishlist.')
    else:
        messages.success(request, f'Added to wishlist!')
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})


# ===== RAZORPAY DUMMY PAYMENT =====
@login_required
def razorpay_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    banks = ['SBI', 'HDFC Bank', 'ICICI Bank', 'Axis Bank', 'Kotak Bank', 'Yes Bank']
    return render(request, 'store/razorpay_payment.html', {
        'order': order,
        'order_id': order_id,
        'amount': order.total_amount,
        'order_number': order.order_number,
        'banks': banks,
    })


@login_required
def confirm_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if request.method == 'POST':
        order.payment_status = 'paid'
        order.payment_method = 'razorpay'
        order.save()
        messages.success(request, f'Payment successful! Order #{order.order_number} confirmed.')
    return redirect('order_success', order_id)
