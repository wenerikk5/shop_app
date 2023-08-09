from .cart import Cart
from .forms import CartAddProductForm


def cart(request):
    cart = Cart(request)
    return {'cart': cart}
