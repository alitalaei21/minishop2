from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.postgres.fields import ArrayField
User = get_user_model()
# Create your models here
def category_image_path(instance, filename):
    return "category/icons/{}/{}".format(instance.name, filename)


def variant_image_path(instance, filename):
    return "product/variants/{}/{}/{}".format(instance.product.title, instance.size_color, filename)

def banner_image_path(instance, filename):
    return "banner/images/{}/{}".format(instance.name, filename)

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='category')
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=category_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class SizeColor(models.Model):
    size = models.IntegerField()
    color = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.size} - {self.color}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    product_id = models.AutoField(primary_key=True)
    description = models.TextField()
    title = models.CharField(max_length=100)
    labor_wage = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    special_sale = models.BooleanField(default=False)
    tags = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="List of tags for this product"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size_color = models.ForeignKey(SizeColor, on_delete=models.CASCADE)
    weight = models.FloatField()
    stock = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    images = ArrayField(
        models.ImageField(upload_to=variant_image_path),
        blank=True,
        default=list,
        help_text="Multiple images for this product variant"
    )

    class Meta:
        unique_together = ('product', 'size_color')

    def __str__(self):
        return f"{self.product.name} - {self.size_color}"

class Order(models.Model):
    PENDING_STATE = "p"
    COMPLETED_STATE = "c"
    ORDER_CHOICES = ((PENDING_STATE, "Pending"), (COMPLETED_STATE, "Completed"))
    status = models.CharField(choices=ORDER_CHOICES, max_length=1, default=PENDING_STATE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE,related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"
    def calculate_total_price(self):
        self.total_price = sum(
            item.quantity * item.price_per_item for item in self.order_items.all()
        )
        self.save()

class OrderItem(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='order_items')
    quantity = models.IntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product}"

class Baner(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=banner_image_path)
    silde = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta:
        unique_together = ('cart', 'product')
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
class Like(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.TextField()
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=30)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"