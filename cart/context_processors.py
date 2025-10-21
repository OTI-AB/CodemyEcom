from .cart import Cart

# Context processor
def cart(request):
  # Return default data from cart
  return {'cart': Cart(request)}