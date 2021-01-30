from django.shortcuts import render, redirect
from django.utils.timezone import now

from MyLibrary.forms import NewAddressForm, NewDeliveryForm
from MyLibrary.models import Book, ProductsInBasket, Order, Address
from MyLibrary.static.static_value import delivery_price


def order_set_address(request):
    if request.method == 'POST':
        form = NewAddressForm(request.POST)
        if form.is_valid():
            form.save()
            address = Address.objects.last()
            return redirect('order_delivery', pk=address.pk)
        else:
            return redirect('order_address')
    else:
        submit_order(request)
        form = NewAddressForm()
        return render(request, 'order/order_address.html', {'form': form},)


def get_delivery_price(delivery_method):
    if delivery_method == 'Kurier':
        return delivery_price.kurier_price
    elif delivery_method == 'Paczkomat':
        return delivery_price.paczkomat_price
    else:
        return delivery_price.poczta_price


def order_set_delivery(request, pk):
    if request.method == 'POST':
        form = NewDeliveryForm(request.POST)
        order_id = request.session.get('order_id')
        order = Order.objects.get(pk=order_id)
        address = Address.object.get(pk=pk)
        form.cleaned_data['order'] = order
        form.cleaned_data['price'] = get_delivery_price(form.delivery_method.__str__())
        form.cleaned_data['address'] = address

        if form.is_valid():
            form.save()
            return redirect('order_summary', pk=order_id)
        return redirect('order_delivery')
    else:
        form = NewDeliveryForm()
        return render(request, 'order/order_delivery.html', {'form': form})


def submit_order(request):
    cart = request.session.get('cart')
    books = list()
    cart_value = 0
    if len(cart) != 0 or cart is None:
        order = Order(order_value=0, date_of_submission=now(), client=request.user)
        order.save()
        for x in cart:
            book = Book.objects.get(pk=x)
            books.append(book)
            cart_value += book.price

            product = ProductsInBasket(product=book, order=order, quantity=1)
            product.save()
        order.order_value = cart_value
        order.save(update_fields=['order_value'])
        request.session['order_id'] = order.pk
    return FileNotFoundError


def order_summary(request, pk):
    order = Order.objects.select_related('address').get(pk=pk)
    return render(request, 'order/order_summary.html', {'order': order})