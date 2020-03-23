from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('filter/<str:category>/', views.filter),
    path('search/', views.search),
    path('search/remove/', views.remove_search),
    path('product/<int:id>/', views.product),
    path('product/<int:id>/add/', views.add_to_cart),
    path('product/<int:id>/remove/', views.remove_from_cart),
    path('checkout/', views.checkout),
    path('checkout/product/<int:id>/remove/', views.remove_from_checkout),
    path('checkout/product/<int:id>/increase/', views.increase_quantity),
    path('checkout/product/<int:id>/decrease/', views.decrease_quantity),
    path('checkout/promo/', views.promo),
    path('checkout/promo/remove/', views.remove_promo),
    path('checkout/order/', views.place_order),
]
