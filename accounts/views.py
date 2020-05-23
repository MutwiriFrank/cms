from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from  django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User

from .filter import OrderFilter
from .models import *
from .forms import *
from .decorators import *


@unauthenticated_user
def registerPage(request):

    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)  # render form again with parameters
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # sent to signals

            # group = Group.objects.get(name='customer')
            # user.groups.add(group)  # adding user to customer group
            # Customer.objects.create(user=user, name=user.username)

            messages.success(request, 'Account was created successfully for' + username)

            return redirect('login')
    context = {
        "form": form
    }
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            print(messages.info(request, 'Wrong Username or Password'))


    context = {}
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all
    total_customers = Customer.objects.count()
    total_orders = orders.count()
    deliv_orders = Order.objects.filter(status="Delivered")
    delivered_orders = deliv_orders.count()
    pend_orders = Order.objects.filter(status="Pending")
    pending_orders = pend_orders.count()

    context = {
        "orders": orders,
        "customers": customers,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "pending_orders": pending_orders
    }

    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    # print('orders:', orders)
    total_orders = orders.count()
    deliv_orders = Order.objects.filter(status="Delivered")
    delivered_orders = deliv_orders.count()
    pend_orders = Order.objects.filter(status="Pending")
    pending_orders = pend_orders.count()

    context = {
        "orders": orders,
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "pending_orders": pending_orders
               }
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)

        if form.is_valid():
            form.save()
    context = {"form": form}
    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()

    context = {
        "products": products
    }

    return render(request, 'accounts/products.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    name = customer.name
    email = customer.email
    phone = customer.phone
    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {
        "customer": customer,
        "name": name,
        "email": email,
        "phone": phone,
        "orders": orders,
        "total_orders": total_orders,
        "myFilter": myFilter,
    }

    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'))
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(instance=customer)
    #form = OrderForm(initial={'customer': customer})

    if request.method == 'POST':
        #form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')


    context = {
        "formset": formset
    }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {
        "form": form
    }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = {
        "item": order
        }

    return render(request, 'accounts/delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createCustomer(request):
    form = CustomerForm

    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'accounts/customer_form.html', context)
