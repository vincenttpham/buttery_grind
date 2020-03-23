from __future__ import unicode_literals
from django.db import models
from user_app.models import User
import datetime

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    discount_price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.0, blank=True)
    quantity = models.IntegerField(default=1)
    image = models.ImageField(upload_to="products/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Rating(models.Model):
    rate = models.IntegerField(default=10)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.user + " " + self.product


class CartProduct(models.Model):
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return "(" + str(self.quantity) + ")" + self.product.name


class Cart(models.Model):
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    quantity = models.IntegerField(default=0)
    promo_code = models.CharField(max_length=255, blank=True)
    promo_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(CartProduct, related_name="cart")

    def __str__(self):
        if self.user:
            return self.user.first_name + " " + self.user.last_name
        return str(self.created_at)


class Order(models.Model):
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zipcode = models.IntegerField(default=0)
    name_on_card = models.CharField(max_length=255, blank=True)
    card_number = models.CharField(max_length=255, blank=True)
    expiration = models.CharField(max_length=255, blank=True)
    cvv = models.CharField(max_length=255, blank=True)
    shipped = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(CartProduct, related_name="order")

    def __str__(self):
        return self.username + " - " + str(self.id)

    def ship(self):
        if self.shipped == True:
            self.shipped = datetime.datetime.now()
            self.save()


class Promo(models.Model):
    code = models.CharField(max_length=255)
    discount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
