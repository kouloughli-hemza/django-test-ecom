from django.shortcuts import render
from store.models import Product, OrderItem, Order


def say_hello(request):
    order_query_set = Order.objects.select_related(
        'customer').prefetch_related('orderitem_set__product')[:5]

    return render(request, 'hello.html',
                  {'name': 'Mosh', 'products': order_query_set})
