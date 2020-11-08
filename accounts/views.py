from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from.models import *
from .forms import OrderForm

# Create your views here.
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    # total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders,'total_orders':total_orders,'delivered':delivered,'pending':pending,'customers':customers}




    return render(request,'accounts/dashboard.html',context)

def product(request):
    products = Product.objects.all()
    return render(request,'accounts/product.html', {'products':products})


def customer(request,pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()
    context = {'customer':customer,'orders':orders,'order_count':order_count}
    return render(request,'accounts/customer.html',context)

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

def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('/')
    context = {'order':order}
    return render(request,'accounts/delete.html',context)