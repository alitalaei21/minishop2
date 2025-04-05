from itertools import product

from django.contrib import admin

from produt.models import Product, Category, Order, OrderItem

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)