from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from shop_app.models import Category, Product, Rating, CartProduct, Cart, Order, Promo
from user_app.models import User, Message
from django.db.models import Q
import datetime
import decimal

# Create your views here.


def index(request):
    request.session['carousel'] = "carousel"
    request.session['page'] = "home"
    products = Product.objects.all()
    expired_carts = Cart.objects.filter(user=None)
    if expired_carts:
        for cart in expired_carts:
            cart_products = cart.products.all()
            if (datetime.datetime.now().timestamp() - cart.updated_at.timestamp()) >= 86400:
                for product_in_cart in cart_products:
                    matching_product = Product.objects.get(
                        name=product_in_cart.product.name, brand=product_in_cart.product.brand)
                    matching_product.quantity += int(product_in_cart.quantity)
                    matching_product.save()
                    product_in_cart.delete()
    if 'category' in request.session:
        if request.session['category'] == 'Shoe':
            products = Product.objects.filter(
                category=Category.objects.get(name='Shoe'))
            if 'search' in request.session:
                products = Product.objects.filter(
                    Q(name__icontains=request.session['search']) | Q(brand__icontains=request.session['search']), category=Category.objects.get(name='Shoe'))
                if not products:
                    messages.error(
                        request, '"' + request.session['search'] + '"' + " does not match any shoes.")
        elif request.session['category'] == 'Hoodie':
            products = Product.objects.filter(
                category=Category.objects.get(name='Hoodie'))
            if 'search' in request.session:
                products = Product.objects.filter(
                    Q(name__icontains=request.session['search']) | Q(brand__icontains=request.session['search']), category=Category.objects.get(name='Hoodie'))
                if not products:
                    messages.error(
                        request, '"' + request.session['search'] + '"' + " does not match any hoodies.")
        elif request.session['category'] == 'Skatewear':
            products = Product.objects.filter(
                category=Category.objects.get(name='Skatewear'))
            if 'search' in request.session:
                products = Product.objects.filter(
                    Q(name__icontains=request.session['search']) | Q(brand__icontains=request.session['search']), category=Category.objects.get(name='Skatewear'))
                if not products:
                    messages.error(
                        request, '"' + request.session['search'] + '"' + " does not match any skatewear.")
        elif request.session['category'] == 'Deck':
            products = Product.objects.filter(
                category=Category.objects.get(name='Deck'))
            if 'search' in request.session:
                products = Product.objects.filter(
                    Q(name__icontains=request.session['search']) | Q(brand__icontains=request.session['search']), category=Category.objects.get(name='Deck'))
                if not products:
                    messages.error(
                        request, '"' + request.session['search'] + '"' + " does not match any decks.")
    elif 'search' in request.session:
        products = Product.objects.filter(
            Q(name__icontains=request.session['search']) | Q(brand__icontains=request.session['search']))
        if not products:
            messages.error(
                request, '"' + request.session['search'] + '"' + " does not match any items.")
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        unread_messages = Message.objects.filter(receiver=user, read=False)
        context = {
            "user": user,
            "products": products,
            "cart": Cart.objects.get(user=user),
            "page_object": page_object,
            "unread_messages": unread_messages,
        }
    elif 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
        if not cart.products.all():
            cart.delete()
            del request.session['cart_id']
        context = {
            "products": products,
            "cart": cart,
            "page_object": page_object
        }
    else:
        context = {
            "products": products,
            "page_object": page_object
        }
    return render(request, "index.html", context)


def product(request, id):
    if 'page' in request.session:
        del request.session['page']
    if 'carousel' in request.session:
        del request.session['carousel']
    product = Product.objects.get(id=id)
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        unread_messages = Message.objects.filter(receiver=user, read=False)
        cart = Cart.objects.get(user=user)
        product_in_cart = cart.products.filter(product=product, cart=cart)
        if product_in_cart:
            product_in_cart = cart.products.get(product=product, cart=cart)
        context = {
            "user": user,
            "product": product,
            "cart": cart,
            "product_in_cart": product_in_cart,
            "unread_messages": unread_messages,
        }
    elif 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
        product_in_cart = cart.products.filter(product=product, cart=cart)
        if product_in_cart:
            product_in_cart = cart.products.get(product=product, cart=cart)
        context = {
            "product": product,
            "cart": cart,
            "product_in_cart": product_in_cart
        }
    else:
        context = {
            "product": product,
        }
    return render(request, "product.html", context)


def checkout(request):
    if 'page' in request.session:
        del request.session['page']
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        unread_messages = Message.objects.filter(receiver=user, read=False)
        cart = Cart.objects.get(user=user)
        cart_products = cart.products.all()
        if not cart_products:
            cart.total = 0
            cart.quantity = 0
            cart.promo_code = ""
            cart.promo_active = False
            cart.save()
        if cart.promo_active:
            promo = Promo.objects.get(code=cart.promo_code, active=True)
            context = {
                "user": user,
                "cart": cart,
                "cart_products": cart_products,
                "promo": promo,
                "unread_messages": unread_messages,
            }
        else:
            context = {
                "user": user,
                "cart": cart,
                "cart_products": cart_products,
                "unread_messages": unread_messages,
            }
    elif 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
        cart_products = cart.products.all()

        #    IF NOT UPDATING CART.QUANTITY DURING ADD/REMOVE FROM CART    #
        ##############
        # for product in cart_products:
        #   cart.quantity += product.quantity
        #   cart.save()

        if not cart_products:
            cart.total = 0
            cart.quantity = 0
            cart.promo_code = ""
            cart.promo_active = False
            cart.save()
        if cart.promo_active:
            promo = Promo.objects.get(code=cart.promo_code, active=True)
            context = {
                "cart": cart,
                "cart_products": cart_products,
                "promo": promo
            }
        else:
            context = {
                "cart": cart,
                "cart_products": cart_products
            }
    else:
        context = {}
    return render(request, "checkout.html", context)


def filter(request, category):
    if category == 'shoe':
        request.session['category'] = 'Shoe'
    elif category == 'hoodie':
        request.session['category'] = 'Hoodie'
    elif category == 'skatewear':
        request.session['category'] = 'Skatewear'
    elif category == 'deck':
        request.session['category'] = 'Deck'
    elif category == 'all':
        if 'category' in request.session:
            del request.session['category']
    return redirect('/')


def search(request):
    request.session['search'] = request.POST['search']
    return redirect('/')


def remove_search(request):
    del request.session['search']
    return redirect('/')


def add_to_cart(request, id):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session["user_id"])
        if not Cart.objects.filter(user=user):
            cart = Cart.objects.create(user=user)
        else:
            cart = Cart.objects.get(user=user)
    elif 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
    else:
        session_cart = Cart.objects.create()
        request.session['cart_id'] = session_cart.id
        cart = Cart.objects.get(id=request.session['cart_id'])
    product = Product.objects.get(id=id)
    id = str(product.id)
    cart_product = CartProduct.objects.create(
        product=product, quantity=request.POST['quantity'])
    cart.products.add(cart_product)
    product_in_cart = CartProduct.objects.get(product=product, cart=cart)
    cart.quantity += int(product_in_cart.quantity)
    cart.save()
    if product.discount_price:
        cart.total += (product.discount_price *
                       decimal.Decimal(product_in_cart.quantity))
        cart.save()
    else:
        cart.total += (product.price *
                       decimal.Decimal(product_in_cart.quantity))
        cart.save()
    messages.info(request, '"' + product.name + '"' + " added to cart.")
    return redirect('/product/'+id)


def remove_from_cart(request, id):
    if 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
    elif 'user_id' in request.session:
        user = User.objects.get(id=request.session["user_id"])
        cart = Cart.objects.get(user=user)
    else:
        session_cart = Cart.objects.create()
        request.session['cart_id'] = session_cart.id
        cart = Cart.objects.get(id=request.session['cart_id'])
    product = Product.objects.get(id=id)
    id = str(product.id)
    product_in_cart = CartProduct.objects.get(product=product, cart=cart)
    cart.quantity -= int(request.POST['quantity'])
    cart.save()
    if int(request.POST['quantity']) == int(product_in_cart.quantity):
        product_in_cart.delete()
    else:
        product_in_cart.quantity -= int(request.POST['quantity'])
        product_in_cart.save()
    if product.discount_price:
        cart.total -= (product.discount_price *
                       decimal.Decimal(request.POST['quantity']))
        cart.save()
    else:
        cart.total -= (product.price *
                       decimal.Decimal(request.POST['quantity']))
        cart.save()
    messages.info(request, '"' + product.name + '"' + " removed from cart.")
    return redirect('/product/'+id)


def remove_from_checkout(request, id):
    if 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
    elif 'user_id' in request.session:
        user = User.objects.get(id=request.session["user_id"])
        cart = Cart.objects.get(user=user)
    product = Product.objects.get(id=id)
    product_in_cart = CartProduct.objects.get(product=product, cart=cart)
    cart.quantity -= int(product_in_cart.quantity)
    cart.save()
    if product.discount_price:
        cart.total -= (product.discount_price *
                       decimal.Decimal(product_in_cart.quantity))
        cart.save()
    else:
        cart.total -= (product.price *
                       decimal.Decimal(product_in_cart.quantity))
        cart.save()
    product_in_cart.delete()
    return redirect('/checkout')


def increase_quantity(request, id):
    if 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
    elif 'user_id' in request.session:
        user = User.objects.get(id=request.session["user_id"])
        cart = Cart.objects.get(user=user)
    product = Product.objects.get(id=id)
    cart_product = CartProduct.objects.get(product=product, cart=cart)
    cart_product.quantity += 1
    cart_product.save()
    cart.quantity += 1
    cart.save()
    if product.discount_price:
        cart.total += product.discount_price
        cart.save()
    else:
        cart.total += product.price
        cart.save()
    return redirect('/checkout')


def decrease_quantity(request, id):
    if 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
    elif 'user_id' in request.session:
        user = User.objects.get(id=request.session["user_id"])
        cart = Cart.objects.get(user=user)
    product = Product.objects.get(id=id)
    cart_product = CartProduct.objects.get(product=product, cart=cart)
    cart_product.quantity -= 1
    cart_product.save()
    cart.quantity -= 1
    cart.save()
    if product.discount_price:
        cart.total -= product.discount_price
        cart.save()
    else:
        cart.total -= product.price
        cart.save()
    return redirect('/checkout')


def promo(request):
    if 'user_id' not in request.session:
        messages.error(request, "Log-in required to redeem promo codes.")
        return redirect('/checkout')
    user = User.objects.get(id=request.session["user_id"])
    cart = Cart.objects.get(user=user)
    cart_products = cart.products.all()
    promo = Promo.objects.filter(code=request.POST["promo"], active=True)
    if cart.promo_active:
        messages.error(request, "Existing promo code already active.")
        return redirect('/checkout')
    elif not promo:
        messages.error(request, "Promo code does not exist or is inactive.")
        return redirect('/checkout')
    elif not cart_products:
        messages.error(
            request, "Please add items into your cart to redeem promo code.")
        return redirect('/checkout')
    else:
        promo = Promo.objects.get(code=request.POST["promo"], active=True)
        cart.total -= promo.discount
        cart.promo_code = promo.code
        cart.promo_active = True
        cart.save()
    return redirect('/checkout')


def remove_promo(request):
    user = User.objects.get(id=request.session['user_id'])
    cart = Cart.objects.get(user=user)
    promo = Promo.objects.get(code=cart.promo_code, active=True)
    cart.total += promo.discount
    cart.promo_code = ""
    cart.promo_active = False
    cart.save()
    return redirect('/checkout')


def place_order(request):
    if 'cart_id' in request.session:
        cart = Cart.objects.get(id=request.session['cart_id'])
        order = Order.objects.create(total=cart.total, first_name=request.POST['first_name'], last_name=request.POST['last_name'], username=request.POST['username'], email=request.POST['email'], address1=request.POST['address1'], address2=request.POST['address2'], city=request.POST['city'],
                                     country=request.POST['country'], state=request.POST['state'], zipcode=request.POST['zipcode'], name_on_card=request.POST['name_on_card'], card_number=request.POST['card_number'], expiration=request.POST['expiration'], cvv=request.POST['cvv'])
    elif 'user_id' in request.session:
        user = User.objects.get(id=request.session["user_id"])
        cart = Cart.objects.get(user=user)
        cart_products = cart.products.all()
        if cart_products:
            order = Order.objects.create(total=cart.total, first_name=request.POST['first_name'], last_name=request.POST['last_name'], username=request.POST['username'], email=request.POST['email'], address1=request.POST['address1'], address2=request.POST['address2'], city=request.POST['city'],
                                         country=request.POST['country'], state=request.POST['state'], zipcode=request.POST['zipcode'], name_on_card=request.POST['name_on_card'], card_number=request.POST['card_number'], expiration=request.POST['expiration'], cvv=request.POST['cvv'], user=user)
        else:
            messages.info(request, "Your cart is empty.")
            return redirect('/checkout')
    cart_products = cart.products.all()
    if cart_products:
        for product in cart_products:
            order.products.add(product)
            order.save()
            db_product = Product.objects.get(id=product.product.id)
            if db_product.quantity == 0:
                product.delete()
                order.delete()
                messages.info(request, '"' + db_product.name +
                              '"' + " is no longer available.")
                return redirect('/checkout')
            elif db_product.quantity < product.quantity:
                product.quantity = db_product.quantity
                product.save()
                order.delete()
                cart.quantity = 0
                cart.quantity += int(product.quantity)
                messages.info(request, '"' + db_product.name +
                              '"' + " exceeded quantity in stock. Item in cart has been adjusted.")
                if product.product.discount_price:

                    cart.total -= product.product.discount_price
                    cart.save()
                else:

                    cart.total -= product.product.price
                    cart.save()
                return redirect('/checkout')
            else:
                cart.products.remove(product)
                cart.save()
                db_product.quantity -= int(product.quantity)
                db_product.save()
                messages.info(request, "Order placed successfully.")
                if 'user_id' in request.session:
                    return redirect('/user')
                else:
                    return redirect('/')
    else:
        order.delete()
        messages.info(request, "Your cart is empty.")
        return redirect('/checkout')
