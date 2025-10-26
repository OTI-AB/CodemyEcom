from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db.models import Q
import json

from cart.cart import Cart


from .models import Product, Category, Profile
from .forms import SignUpForm, UpdateUserForm, UpdatePasswordForm, UserInfoForm

def search(request):
  # Did user fill out form?
  if request.method == 'POST':
    searched = request.POST['searched']
    # Query the db
    searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
    # Test for null
    if not searched:
      messages.warning(request, 'Product not found, try a different search.')
      return redirect('search')
    return render(request, "search.html", {'searched': searched})
  else:
    return render(request, 'search.html', {})

def update_info(request):
  if request.user.is_authenticated:
    current_user = Profile.objects.get(user__id=request.user.id)

    form = UserInfoForm(request.POST or None, instance=current_user)

    if form.is_valid():
      form.save()
      messages.success(request, 'Your info was successfuly updated')
      return redirect('home')
    return render(request, 'update_info.html', {'form': form})


  else:
    messages.secondary(request, 'Please login to update your information')
    return redirect('login')

def update_password(request):
  if request.user.is_authenticated:
    current_user = request.user
    # Did they fill out the form
    if request.method == 'POST':
      form = UpdatePasswordForm(current_user, request.POST)
      if form.is_valid():
        form.save()
        messages.success(request, 'Password changed, please note new password.')
        login(request, current_user)
        return redirect('update_user')
      else:
        for error in list(form.errors.values()):
          messages.error(request, error)
          return redirect('update_password')
    else:
      form = UpdatePasswordForm(current_user)
      return render(request, 'update_password.html', {'form': form})


  else:
    messages.secondary(request, 'Please login to update your information')
    return redirect('login')
  

def update_user(request):
  if request.user.is_authenticated:
    current_user = User.objects.get(id=request.user.id)
    user_form = UpdateUserForm(request.POST or None, instance=current_user)

    if user_form.is_valid():
      user_form.save()
      login(request, current_user)
      messages.success(request, 'Your profile was successfuly updated')
      return redirect('home')
    return render(request, 'update_user.html', {'user_form': user_form})
  else:
    messages.secondary(request, 'Please login to update your information')
    return redirect('login')

def category_summary(request):
  categories = Category.objects.all()
  products = Product.objects.all()

  return render(request, 'category_summary.html', {'categories': categories, 'products': products})
  
 
def category(request, cat):
  cat = cat.replace('-', ' ')
  try:
    category = Category.objects.get(name=cat)
    products = Product.objects.filter(category=category)
    return render(request, 'category.html', {'products': products, 'category': category})
  except:
    messages.warning(request, 'Sorry, that category does not exist')
    return redirect('home')

def product(request, pk):
  product = Product.objects.get(id=pk)
  return render(request, 'product.html', {'product': product})

def home(request):
  products = Product.objects.all()
  return render(request, 'home.html', {'products': products})

def about(request):
  return render(request, 'about.html', {})

def login_user(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)

      # Retrieve user's cart from profile
      current_user = Profile.objects.get(user__id=request.user.id)
      saved_cart = current_user.old_cart
      # Convert back to python dictionary
      if saved_cart:
        # Convert using JSON
        converted_cart = json.loads(saved_cart)
        # Add the loaded cart dictionary to our session
        cart = Cart(request)
        # Loop thru the cart, add items from the db
        for key, value in converted_cart.items():
          cart.db_add(product=key, quantity=value)


      messages.success(request, 'Successful login, Welcome.')
      return redirect('home')
    else:
      messages.error(request, 'User credentials error')
      return redirect('login')
  else:
    return render(request, 'login.html', {})

def logout_user(request):
  logout(request)
  messages.success(request, 'You are logged out...Thanks for shopping with us.')
  return redirect('home')

def register_user(request):
  form = SignUpForm()
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data['username']
      password = form.cleaned_data['password1']
      first_name = form.cleaned_data['first_name']
      # Log in user
      user = authenticate(username=username, password=password)
      login(request,user)
      messages.success(request, f'Successful Registration...Please complete your information. {first_name}')
      return redirect('update_info')
    else:
      messages.warning(request, 'Registration error.. please try again')
      return redirect('register')
  else:
     return render(request, 'register.html', {'form': form})