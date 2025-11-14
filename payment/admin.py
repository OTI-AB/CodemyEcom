from django.contrib import admin
from django.contrib.auth.models import User

from .models import ShippingAddress, Order, OrderItem

# Register model for admin section
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

# Create OrderItem Inline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

# Extend order model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped", "date_shipped", "invoice", "paid"]
    inlines = [OrderItemInline]

admin.site.unregister(Order)

admin.site.register(Order, OrderAdmin)
