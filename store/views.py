from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db.models import Count, Q

from .models import Product, Category
from .forms import SignUpForm

def category_summary(request):
  categories = Category.objects.all()
  products = Product.objects.all()
  cats=Category.objects.all().values_list('id')
  prods=Product.objects.values_list('name')

  return render(request, 'category_summary.html', {'categories': categories, 'products': products, 'prods': prods, 'cats': cats})
  
 
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
      messages.success(request, 'Successful login, Welcome.')
      return redirect('home')
    else:
      messages.danger(request, 'User credentials error')
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
      messages.success(request, f'Successful Registration...Welcome {first_name}')
      return redirect('home')
    else:
      messages.warning(request, 'Registration error.. please try again')
      return redirect('register')
  else:
     return render(request, 'register.html', {'form': form})