from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from inventory.models import ProductItem

from .cart import Cart
from .forms import CartAddProductForm
from inventory import views, models
from inventory.recommender import Recommender


@require_POST
def cart_add(request, sku):
    cart = Cart(request)
    product = get_object_or_404(ProductItem, sku=sku)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(ProductItem, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    products = []

    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
                                        'quantity': item['quantity'],
                                        'override': True})
        products.append(item.get('product'))
        # print('=====cart item:', item)

    r = Recommender()
    recommended_products = r.suggest_products_for(products, 4)

    context = {
        'cart': cart,
        'recommended_products': recommended_products,
    }
    return render(request, 'cart/detail.html', context)
