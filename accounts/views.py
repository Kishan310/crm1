from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate ,login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.

from.models import *
from .forms import OrderForm , CreatuserForm
from .filters import OrderFilter
from .decorators import unauthenticated_user,allowed_users,admin_only


def registerpage(request):
        form = CreatuserForm()
        if request.method == 'POST':
            form = CreatuserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')

                group = Group.objects.get(name='customer')
                user.groups.add(group)

                messages.success(request, 'Account was created for ' + username)

                return redirect('login')

        context={'form':form}
        return render(request,'accounts/register.html',context)
@unauthenticated_user
def loginpage(request):
        if request.method=='POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request,username = username,password = password)

            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.info(request,'Username Or Password is incorrect')
                return render(request, 'accounts/login.html')

        context={}
        return render(request ,'accounts/login.html',context)

def logoutuser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    # total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders,'total_orders':total_orders,'delivered':delivered,'pending':pending,'customers':customers}
    return render(request,'accounts/dashboard.html',context)

def userpage(request):
    context={}
    return render(request,'accounts/user.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product(request):
    products = Product.objects.all()
    return render(request,'accounts/product.html', {'products':products})



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET,queryset=orders)
    orders = myFilter.qs

    context = {'customer':customer,'orders':orders,'order_count':order_count,'myFilter':myFilter}
    return render(request,'accounts/customer.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOreder(request,pk):
    OrderFormSet = inlineformset_factory(Customer,Order,fields=('product','status'),extra=10)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
    # forms = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        # print('Printing POST:' , request.POST)
        # forms = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)

        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'formset':formset,}
    return render(request,'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):
    order = Order.objects.get(id=pk)
    forms = OrderForm(instance=order)
    if request.method == 'POST':
        forms = OrderForm(request.POST,instance=order)
        if forms.is_valid():
            forms.save()
            return redirect('/')
    contex = {'forms':forms}
    return render(request,'accounts/order_form.html',contex)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('/')
    context = {'order':order}
    return render(request,'accounts/delete.html',context)