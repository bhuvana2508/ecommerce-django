from .models import Cart

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            count = cart.get_item_count()
        except:
            pass
    return {'cart_count': count}
