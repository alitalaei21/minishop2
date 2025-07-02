from django.contrib import admin
from produt.models import Product, Category, Order, OrderItem, Baner, ProductVariant, Like

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Baner)
admin.site.register(ProductVariant)
admin.site.register(Like)