from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from user_app.models import User, UserManager, Message
from shop_app.models import Category, Product, Rating, CartProduct, Cart, Order, Promo
from django.db.models import Q
import bcrypt
import datetime
from datetime import timedelta
import random

# Create your views here.


def login(request):
    if 'page' in request.session:
        del request.session['page']
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' in request.session:
        return redirect('/user')
    return render(request, "login.html")


def log(request):
    user = User.objects.filter(email=request.POST["email"])
    if not user:
        messages.error(request, "Email address not found.")
        return redirect("/user/login")
    logged_user = user[0]
    if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
        request.session["user_id"] = logged_user.id
        return redirect("/")
    else:
        messages.error(request, "Invalid email/password combination.")
        return redirect("/user/login")


def logout(request):
    request.session.flush()
    request.session.clear()
    return redirect("/")


def register(request):
    if 'page' in request.session:
        del request.session['page']
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' in request.session:
        return redirect('/user')
    return render(request, "register.html")


def reg(request):
    errors = User.objects.registration_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect("/user/register")
    else:
        password = request.POST["password"]
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(
            first_name=request.POST["first_name"], last_name=request.POST["last_name"], username=request.POST["username"], email=request.POST["email"], password=pw_hash)
        cart = Cart.objects.create(user=user)
        message = Message.objects.create(
            body='Thank you for registering with The Buttery Grind. As a thank-you gift for shopping with us, enter code "BUTTERY" at checkout to redeem $20 off your first order.', receiver=user)
        request.session["user_id"] = user.id
        return redirect("/")


def orders(request):
    request.session['page'] = "account"
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' not in request.session:
        return redirect('/user/login')
    user = User.objects.get(id=request.session['user_id'])
    cart = Cart.objects.get(user=user)
    cart_products = cart.products.all()
    if not cart_products:
        cart.total = 0
        cart.quantity = 0
        cart.promo_code = ""
        cart.promo_active = False
        cart.save()
    if 'sort_by' in request.session:
        orders = Order.objects.filter(
            user=user, shipped=False).order_by('created_at')
    else:
        orders = Order.objects.filter(
            user=user, shipped=False).order_by('-created_at')
    eta = random.randrange(2, 5)
    unread_messages = Message.objects.filter(receiver=user, read=False)
    context = {
        "user": user,
        "cart": Cart.objects.get(user=user),
        "orders": orders,
        "eta": eta,
        "unread_messages": unread_messages,
    }
    return render(request, "orders.html", context)


def sort_by(request):
    if request.POST['sort_by'] == 'oldest':
        request.session['sort_by'] = 'oldest'
    elif request.POST['sort_by'] == 'newest':
        del request.session['sort_by']
    return redirect('/user')


def history(request):
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' not in request.session:
        return redirect('/user/login')
    user = User.objects.get(id=request.session['user_id'])
    orders = Order.objects.filter(user=user, shipped=False)
    shipped_orders = Order.objects.filter(user=user, shipped=True)
    today = datetime.datetime.today()
    yesterday = datetime.datetime.today() - timedelta(days=1)
    orders_today = Order.objects.filter(
        user=user, shipped=True, updated_at=today)
    orders_yesterday = Order.objects.filter(
        user=user, shipped=True, updated_at=yesterday)
    old_orders = Order.objects.filter(
        user=user, shipped=True, updated_at__lt=yesterday)
    unread_messages = Message.objects.filter(receiver=user, read=False)
    context = {
        "user": user,
        "cart": Cart.objects.get(user=user),
        "orders": orders,
        "shipped_orders": shipped_orders,
        "orders_today": orders_today,
        "orders_yesterday": orders_yesterday,
        "old_orders": old_orders,
        "unread_messages": unread_messages,
    }
    return render(request, "history.html", context)


def message_view(request):
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' not in request.session:
        return redirect('/user/login')
    user = User.objects.get(id=request.session['user_id'])
    unread_messages = Message.objects.filter(receiver=user, read=False)
    orders = Order.objects.filter(user=user, shipped=False)
    if 'user_search' in request.session:
        user_list = User.objects.filter(
            Q(first_name__icontains=request.session['user_search']) | Q(last_name__icontains=request.session['user_search']) | Q(username__icontains=request.session['user_search']))
        if not user_list:
            messages.error(
                request, '"' + request.session['user_search'] + '"' + " does not match any users.")
    else:
        user_list = User.objects.filter().exclude(id=user.id).order_by('last_name')
    if 'other_user' in request.session:
        other_user = User.objects.get(id=request.session['other_user'])
        user_messages = Message.objects.filter(
            sender__id=request.session['other_user'], receiver=user)
        chat_messages = Message.objects.filter(
            Q(sender__id=request.session['other_user'], receiver=user) | Q(sender=user, receiver__id=request.session['other_user'])).order_by('created_at')
        context = {
            "user": user,
            "other_user": other_user,
            "user_list": user_list,
            "cart": Cart.objects.get(user=user),
            "orders": orders,
            "user_messages": user_messages,
            "unread_messages": unread_messages,
            "chat_messages": chat_messages,
        }
    else:
        context = {
            "user": user,
            "user_list": user_list,
            "cart": Cart.objects.get(user=user),
            "orders": orders,
            "unread_messages": unread_messages,
        }
    return render(request, "messages.html", context)


def read_message(request, id):
    user = User.objects.get(id=request.session['user_id'])
    other_user = User.objects.get(id=id)
    request.session['other_user'] = other_user.id
    chat_messages = Message.objects.filter(sender=other_user, receiver=user)
    for message in chat_messages:
        message.read = True
        message.save()
    return redirect("/user/messages")


def send_message(request):
    user = User.objects.get(id=request.session['user_id'])
    receiver = User.objects.get(id=request.session['other_user'])
    message = Message.objects.create(
        body=request.POST['body'], sender=user, receiver=receiver)
    return redirect("/user/messages")


def user_search(request):
    request.session['user_search'] = request.POST['user_search']
    return redirect('/user/messages')


def user_remove_search(request):
    del request.session['user_search']
    return redirect('/user/messages')


def account(request):
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' not in request.session:
        return redirect('/user/login')
    user = User.objects.get(id=request.session['user_id'])
    orders = Order.objects.filter(user=user, shipped=False)
    unread_messages = Message.objects.filter(receiver=user, read=False)
    context = {
        "user": user,
        "cart": Cart.objects.get(user=user),
        "orders": orders,
        "unread_messages": unread_messages,
    }
    return render(request, "account.html", context)


def billing(request):
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' not in request.session:
        return redirect('/user/login')
    user = User.objects.get(id=request.session['user_id'])
    orders = Order.objects.filter(user=user, shipped=False)
    unread_messages = Message.objects.filter(receiver=user, read=False)
    context = {
        "user": user,
        "cart": Cart.objects.get(user=user),
        "orders": orders,
        "unread_messages": unread_messages,
    }
    return render(request, "billing.html", context)


def notifications(request):
    if 'carousel' in request.session:
        del request.session['carousel']
    if 'user_id' not in request.session:
        return redirect('/user/login')
    user = User.objects.get(id=request.session['user_id'])
    orders = Order.objects.filter(user=user, shipped=False)
    unread_messages = Message.objects.filter(receiver=user, read=False)
    context = {
        "user": user,
        "cart": Cart.objects.get(user=user),
        "orders": orders,
        "unread_messages": unread_messages,
    }
    return render(request, "notifications.html", context)


def update_account(request):
    user = User.objects.filter(id=request.session['user_id'])
    logged_user = user[0]
    errors = User.objects.update_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect("/user/settings/account/")
    if bcrypt.checkpw(request.POST['current_password'].encode(), logged_user.password.encode()):
        user = User.objects.get(id=request.session['user_id'])
        password = request.POST["password"]
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user.first_name = request.POST["first_name"]
        user.last_name = request.POST["last_name"]
        user.username = request.POST["username"]
        user.email = request.POST["email"]
        user.password = pw_hash
        user.save()
        messages.info(request, "Successfully updated account info.")
        return redirect("/user/settings/account")
    else:
        messages.error(request, "Current password is incorrect.")
        return redirect("/user/settings/account")


def update_billing(request):
    user = User.objects.get(id=request.session['user_id'])
    user.country = request.POST["country"]
    user.address1 = request.POST["address1"]
    user.address2 = request.POST["address2"]
    user.city = request.POST["city"]
    user.state = request.POST["state"]
    user.zipcode = request.POST["zipcode"]
    user.save()
    messages.info(request, "Successfully updated billing info.")
    return redirect("/user/settings/billing")
