from django.contrib import admin
from shop_app.models import Category, Product, Rating, CartProduct, Cart, Order, Promo

# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Rating)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Promo)
