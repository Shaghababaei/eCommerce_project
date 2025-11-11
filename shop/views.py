from django.shortcuts import render
from decimal import Decimal
from .models import Product,Category
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})

def product_list(request, category_id=None):
    categories = Category.objects.all()
    products = Product.objects.all()

    selected_category = None
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=selected_category)

    context = {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from decimal import Decimal

def _get_cart(request):
    return request.session.get('cart', {})

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def add_to_cart(request, product_id):
    cart = _get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(request, cart)
    return redirect('cart_detail')

def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect('cart_detail')

def cart_detail(request):
    cart = _get_cart(request)

    if request.method == 'POST':
        updated = {}
        for k, v in request.POST.items():
            if not k.startswith('qty_'):
                continue
            pid = k.split('qty_')[-1]
            try:
                qty = int(v)
            except ValueError:
                qty = 0
            if qty > 0:
                updated[pid] = qty
        cart = updated
        _save_cart(request, cart)
        return redirect('cart_detail')

    items = []
    total = Decimal('0.00')
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue
        subtotal = product.price * int(quantity)
        total += subtotal
        items.append({
            'product': product,
            'quantity': int(quantity),
            'subtotal': subtotal,
        })

    context = {
        'cart_items': items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)
