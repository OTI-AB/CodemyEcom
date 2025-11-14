from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    # Add 10 sec. delay for PayPal to send IPN data
    time.sleep(10)
    # Get the data that paypal sends
    paypal_obj = sender
    # Grab the invoice
    my_Invoice = str(paypal_obj.invoice)

    # Match the Paypal invoice to the Order invoice
    # Look up the order
    my_Order = Order.objects.get(invoice=my_Invoice)

    # Record that the order was paid
    my_Order.paid = True

    my_Order.save()
 