from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User

from store.models import Category, Customer, Product, Order, Profile

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)

# Add profile info to user info
class ProfileInline(admin.StackedInline):
  model = Profile

# Extend user model
class UserAdmin(admin.ModelAdmin):
  model = User
  field = ['username', 'first_name', 'last_name', 'email',]
  inlines = [ProfileInline]

# Unregister old way
admin.site.unregister(User)

# Rer-register new way
admin.site.register(User, UserAdmin)
