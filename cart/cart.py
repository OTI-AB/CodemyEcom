from store.models import Product


class Cart():
  def __init__(self, request):
    self.session = request.session

    # Get current session key if it exists
    cart = self.session.get('session_key')

    # If new user, no session key. Create one
    if 'session_key' not in request.session:
      cart = self.session['session_key'] = {}

    # Make sure cart is available on all pages of site
    self.cart = cart

  def add(self, product, quantity):
    product_id = str(product.id)
    product_qty = str(quantity)

    # Logic
    if product_id in self.cart:
      pass
    else:
      self.cart[product_id] = int(product_qty)
      # self.cart[product_id] = {'price': str(product.price)}
    
    self.session.modified = True

  def __len__(self):
    return len(self.cart)
  
  def get_prods(self):
    # Get ids in cart
    product_ids = self.cart.keys()
    # Use ids to lookup products in db
    products = Product.objects.filter(id__in=product_ids)
    return products
  
  def get_quants(self):
    # Get ids in cart
    quantities = self.cart
    return quantities
 
  def update(self, product, quantity):
    product_id = str(product)
    product_qty = int(quantity)

    # Get cart
    ourcart = self.cart
    # Update cart dictionary
    ourcart[product_id] = product_qty

    self.session.modified = True

    new_cart = self.cart
    return new_cart

  def delete(self, product):
    product_id = str(product)
    # Delete item
    if product_id in self.cart:
      del self.cart[product_id]

    self.session.modified = True

  def cart_total(self):
    # Get product ids {'4': 2, '3': 1}
    product_ids = self.cart.keys()
    # Look up keys in product db model
    products = Product.objects.filter(id__in=product_ids)
    quantities = self.cart
    total = 0

    for key, value in quantities.items():
      key = int(key)
      for product in products:
        if product.id == key:
          if product.is_sale:
            total += (value * product.sale_price)
          else:
            total += (value * product.price)
    return total