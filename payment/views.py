from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
import datetime

# Import paypal
from django.urls import reverse
from django.conf import settings
import uuid #Unique user
from paypal.standard.forms import PayPalPaymentsForm

from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from store.models import Product, Profile

def orders(request, pk):
  if request.user.is_authenticated and request.user.is_superuser:
    # Get the order
    order = Order.objects.get(id=pk)
    # Get order items
    order_items = OrderItem.objects.filter(order=pk)
    if request.POST:
      status = request.POST['ship_status']
      # Check true or false
      if status == 'true':
        # # Get the order
        order = Order.objects.filter(id=pk)
        now = datetime.datetime.now()
        # Update status
        order.update(shipped=True, date_shipped=now)
      else:
        # # Get the order
        order = Order.objects.filter(id=pk)
        # Update status
        order.update(shipped=False)
      messages.success(request, 'Ship Status Toggled')
      return redirect('home')

    return render(request, 'payment/orders.html', {'order': order, 'order_items': order_items})
  else:
    messages.warning(request, 'Access Forbidden!')
    return redirect('home')

def not_shipped_dash(request):
  if request.user.is_authenticated and request.user.is_superuser:
    orders = Order.objects.filter(shipped=False)
    if request.POST:
      num = request.POST['num']

      order = Order.objects.filter(id=num)
      now = datetime.datetime.now()
        # Update status
      order.update(shipped=True, date_shipped=now)
      
      messages.success(request, 'Ship Status Toggled')
      return redirect('home')
    return render(request, 'payment/not_shipped_dash.html', {'orders': orders})
  else:
    messages.warning(request, 'Access Forbidden!')
    return redirect('home')


def shipped_dash(request):
  if request.user.is_authenticated and request.user.is_superuser:
    orders = Order.objects.filter(shipped=True)
    if request.POST:
      num = request.POST['num']

      order = Order.objects.filter(id=num)
      now = datetime.datetime.now()
        # Update status
      order.update(shipped=False)
      
      messages.success(request, 'Ship Status Toggled')
      return redirect('home')
    return render(request, 'payment/shipped_dash.html', {'orders': orders})
  else:
    messages.warning(request, 'Access Forbidden!')
    return redirect('home')


def process_order(request):
  if request.POST:
    # Get the right cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    # Get billing info from form
    payment_form = PaymentForm(request.POST or None)
    # Get shipping session data
    my_shipping = request.session.get('my_shipping')

    # Gather Order Data
    full_name = my_shipping['shipping_full_name']
    email = my_shipping['shipping_email']
    # Create shipping address from session data
    shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_province']}\n{my_shipping['shipping_country']}\n{my_shipping['shipping_postal_code']}\n"

    amount_paid = totals

    # Create the order

    if request.user.is_authenticated:
      user = request.user
      create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid,)
      create_order.save()

      # Add order items
      # Order ID
      order_id = create_order.pk
      
      for product in cart_products():
        # Product(s) ID
        product_id = product.id
        # Product(s) price
        if product.is_sale:
          price = product.sale_price
        else:
          price = product.price
        # Quantity
        for key, value in quantities().items():
          if int(key) == product.id:
            # Create order item
            create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price,)
            create_order_item.save()
      # Delete cart
      for key in list(request.session.keys()):
        # Delete the key
        if key == 'session_key':
          # Delete the key
          del request.session[key]
      # Delete cart from db (old_cart field)
      current_user = Profile.objects.filter(user__id= request.user.id)
      # Delete shopping cart in db (old_cart field)
      current_user.update(old_cart="")


      messages.success(request, 'Order recieved, thank you!')
      return redirect('home')
    else:
      create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid,)
      create_order.save()
            # Add order items
      # Order ID
      order_id = create_order.pk
      
      for product in cart_products():
        # Product(s) ID
        product_id = product.id
        # Product(s) price
        if product.is_sale:
          price = product.sale_price
        else:
          price = product.price
        # Quantity
        for key, value in quantities().items():
          if int(key) == product.id:
            # Create order item
            create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price,)
            create_order_item.save()
      # Delete cart
      for key in list(request.session.keys()):
        if key == 'session_key':
          # Delete the key
          del request.session[key]

      messages.success(request, 'Order recieved, thank you!')
      return redirect('home')
  else:
    messages.warning(request, 'Access Forbidden!')
    redirect('home')
  return render(request, 'payment/process_order.html', {})

def billing_info(request):
  if request.POST:
    # Get the right cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    # Create a session with Shipping Data
    my_shipping = request.POST
    request.session['my_shipping'] = my_shipping

    # Gather Order Data
    full_name = my_shipping['shipping_full_name']
    email = my_shipping['shipping_email']
    # Create shipping address from session data
    shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_province']}\n{my_shipping['shipping_country']}\n{my_shipping['shipping_postal_code']}\n"

    amount_paid = totals

    # Get the host
    host = request.get_host()

    # Create Inv Number
    my_Invoice = str(uuid.uuid4())

   

    # Create PayPal form dictionary
    paypal_dict = {
      'business': settings.PAYPAL_RECEIVER_EMAIL,
      'amount': totals,
      'item_name': 'Item Order',
      'no_shipping': 2,
      'invoice': my_Invoice,
      'currency_code': 'CAD',
      'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
      'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
      'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
    }

    paypal_form = PayPalPaymentsForm(initial=paypal_dict)

    # Check if user is logged in
    if request.user.is_authenticated:
      # Logged In
      # Get billing form
      billing_form = PaymentForm()

       # Create an Order
    # ??????????????????????????????????????????
      user = request.user
      create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice,)
      create_order.save()

      # Add order items
      # Order ID
      order_id = create_order.pk
      
      for product in cart_products():
        # Product(s) ID
        product_id = product.id
        # Product(s) price
        if product.is_sale:
          price = product.sale_price
        else:
          price = product.price
        # Quantity
        for key, value in quantities().items():
          if int(key) == product.id:
            # Create order item
            create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price,)
            create_order_item.save()
 
      # Delete cart from db (old_cart field)
      current_user = Profile.objects.filter(user__id= request.user.id)
      # Delete shopping cart in db (old_cart field)
      current_user.update(old_cart="")

      return render(request, 'payment/billing_info.html', {"paypal_form":paypal_form,'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form, })
    else:
      # Not Logged In
      create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice)
      create_order.save()
      # Add order items
      # Order ID
      order_id = create_order.pk
      
      for product in cart_products():
        # Product(s) ID
        product_id = product.id
        # Product(s) price
        if product.is_sale:
          price = product.sale_price
        else:
          price = product.price
        # Quantity
        for key, value in quantities().items():
          if int(key) == product.id:
            # Create order item
            create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price,)
            create_order_item.save()
  
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      billing_form = PaymentForm()
    return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals,})
  else:
    messages.warning(request, 'Access Forbidden')
    return redirect('home')

def payment_success(request):
  # Delete cart from browser
    # Get the right cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    k = ''
    v = ''

      
    for key in list(request.session.keys()):
      if key == 'session_key':
          # Delete the key
        del request.session[key]

    return render(request, 'payment/payment_success.html', { "cart_products": cart_products, "totals": totals, "quantities": quantities, "k": k, "v": v})

def payment_failed(request):
  return render(request, 'payment/payment_failed.html', {})

def checkout(request):
# Get the right cart
  cart = Cart(request)
  cart_products = cart.get_prods
  quantities = cart.get_quants
  totals = cart.cart_total()

  if request.user.is_authenticated:
    # Logged in user
    shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
    shipping_form = ShippingForm(request.POST or None, instance=shipping_user,)
    return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form, })  
  else:
    # Guest
    shipping_form = ShippingForm(request.POST or None,)
    return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form': shipping_form })  
