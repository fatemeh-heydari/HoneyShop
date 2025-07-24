from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from .forms import ShippingForm
from .models import ShippingAddress, Order, OrderItem
from django.contrib import messages
from shop.models import Product, Profile
from django.contrib.auth.models import User


def payment_success(request):
    return render(request, 'payment/payment_success.html', {})




def chekout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    total = cart.get_total()

    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id = request.user.id)
        shipping_form = ShippingForm(request.POST or None,instance= shipping_user)
        return render(request, 'payment/chekout.html', {'cart_products':cart_products , 'quantities':quantities, 'total':total, 'shipping_form':shipping_form})
    else:
        shipping_form = ShippingForm(request.POST or None)
        return render(request, 'payment/chekout.html', {'cart_products':cart_products , 'quantities':quantities, 'total':total, 'shipping_form':shipping_form})
    




def confirm_order (request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        total = cart.get_total()

        user_shipping = request.POST
        request.session['user_shipping'] = user_shipping

        return render(request, 'payment/confirm_order.html', {'cart_products':cart_products , 'quantities':quantities, 'total':total, 'shipping_info':user_shipping})

    else:
        messages.success(request, 'دسترسی به این صفحه امکان پذیر نمیباشد',{})
        return redirect('home')
        # این قطعه کد باعث میشود کاربر فقط از طریق دکمه ی صورتحساب بتواند وارد صفحه ی چک اوت شود و اگر از طریق دیگر مثل سرچ کردن یوارال اقدام به ورود کرد وارد صفحه نشود و با اخطار مواجه شود
    # return render(request, 'payment/confirm_order.html', {})


def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        total = cart.get_total()

        user_shipping = request.session.get('user_shipping')

        # برای ثبت سفارش به مقادیر مدل اوردر در مدلهای پی منت نیاز داریم
        full_name = user_shipping['shipping_full_name']
        email = user_shipping['shipping_email']
        full_address = f"{user_shipping['shipping_country']}\n{user_shipping['shipping_city']}\n{user_shipping['shipping_state']}\n{user_shipping['shipping_address']}\n{user_shipping['shipping_zipcode']}"



        # نمایش اطلاعات کاربری که وارد حساب کاربری خود شده است در صفحه صورتحساب
        if request.user.is_authenticated:
            user = request.user
            new_order = Order(
                user = user,
                full_name = full_name,
                email = email,
                shipping_address = full_address,
                amount_paid = total,
            )
            new_order.save()


            orders = get_object_or_404(Order, id=new_order.pk)


            # نمایش محصولات سفارش داده شده و مشخصات انها در صفحه صورتحساب
            for product in cart_products:
                prod = get_object_or_404(Product, id=product.id)

                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                for k,v in quantities.items():
                    if int(k) == product.id:
                        new_item = OrderItem(
                            order = orders,
                            product = prod,
                            price = price,
                            quantity = v,
                            user = user
                        )
                        new_item.save()

            for key in list(request.session.keys()):
                if key == 'session_key':
                    del request.session[key]
                    #  برای حذف محصولاتی که خریداری شده اند از سبد خرید میباشد

            cu = Profile.objects.filter(user__id = request.user.id)
            cu.update(old_cart="")


            messages.success(request, 'سفارش ثبت شد',{})
            return redirect('home')
        else:
            new_order = Order(
                full_name = full_name,
                email = email,
                shipping_address = full_address,
                amount_paid = total,
            )
            new_order.save()


            orders = get_object_or_404(Order, id=new_order.pk)

            for product in cart_products:
                prod = get_object_or_404(Product, id=product.id)

                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                for k,v in quantities.items():
                    if int(k) == product.id:
                        new_item = OrderItem(
                            order = orders,
                            product = prod,
                            price = price,
                            quantity = v,
                        )
                        new_item.save()
            for key in list(request.session.keys()):
                if key == 'session_key':
                    del request.session[key]

            messages.success(request, 'سفارش ثبت شد',{})
            return redirect('home')
    else:
        messages.success(request, 'دسترسی به این صفحه امکان پذیر نمیباشد',{})
        return redirect('home')



