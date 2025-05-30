from rest_framework import serializers

from produt.models import Category, OrderItem, Order, Baner, CartItem, Cart, Like, Comment, \
    Address, Product, ProductImage, ProductVariant, SizeColer
from goldapi.goldapifun import get_gold_price
import logging

logger = logging.getLogger(__name__)
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'product', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']
class SizeColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeColer
        fields = ['id', 'size', 'coler']

class ProductVariantSerializer(serializers.ModelSerializer):
    size_coler = SizeColorSerializer()

    class Meta:
        model = ProductVariant
        fields = ['id', 'size_coler', 'weight', 'stock']

    def create(self, validated_data):
        size_coler_data = validated_data.pop('size_coler')
        size_coler, created = SizeColer.objects.get_or_create(**size_coler_data)
        variant = ProductVariant.objects.create(size_coler=size_coler, **validated_data)
        return variant

    def update(self, instance, validated_data):
        size_coler_data = validated_data.pop('size_coler', None)
        if size_coler_data:
            size_coler, created = SizeColer.objects.get_or_create(**size_coler_data)
            instance.size_coler = size_coler
        instance.weight = validated_data.get('weight', instance.weight)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'
    def create(self, validated_data):
        variants_data = validated_data.pop('variants')
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)

        for variant_data in variants_data:
            size_coler_data = variant_data.pop('size_coler')
            size_coler, created = SizeColer.objects.get_or_create(**size_coler_data)
            ProductVariant.objects.create(product=product, size_coler=size_coler, **variant_data)

        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', None)
        images_data = validated_data.pop('images', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if variants_data is not None:

            instance.variants.all().delete()
            for variant_data in variants_data:
                size_coler_data = variant_data.pop('size_coler')
                size_coler, created = SizeColer.objects.get_or_create(**size_coler_data)
                ProductVariant.objects.create(product=instance, size_coler=size_coler, **variant_data)

        if images_data is not None:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)

        return instance
    def get_likes_count(self, obj):
        return obj.likes.count()
    def gold_api_price(self):
        try:
            response = get_gold_price()
            if response is None or response == 0:
                logger.warning("Could not get gold price, using default value")
                return 0
            return float(response)
        except Exception as e:
            logger.error(f"Error getting gold price in ProductSerializer: {str(e)}")
            return 0
    def get_final_price(self, obj):
        price_gold = self.gold_api_price()
        gold_price = (price_gold * obj.weight)
        gold_price = gold_price + (gold_price * (obj.labor_wage / 100))
        gold_price = gold_price + (gold_price * 0.09) #tax
        gold_price = gold_price + (gold_price * 0.07) #profit

        if obj.discount > 0 :
            discount = gold_price * (obj.discount / 100)
            return int(gold_price - discount)
        return int(gold_price)


    # def get_discounted_price(self, obj):
    #     return obj.discounted_price()
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_id','name','image',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_per_item', 'order']
class OrderSerializer(serializers.ModelSerializer):
    order_items_data = OrderItemSerializer(many=True, write_only=True)
    order_items_detail = OrderItemSerializer(many=True, read_only=True,source='order_items_data')
    class Meta:
        model = Order
        fields = ('id','customer','order_date','total_price','order_items_data','order_items_detail',)
    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order=Order.objects.create(**validated_data)
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        order.calculate_total_price()
        return order
class BanerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baner
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    Product = ProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ['id','product','quantity']
class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = CartItem
        fields = ['product_id','quantity']
    def create(self, validated_data):
        cart = self.context['cart']
        product_id = validated_data['product_id']
        quantity = validated_data['quantity']
        item, created = CartItem.objects.get_or_create(cart=cart,product=product_id)
        if not created:
            item.quantity += quantity
            item.save()
        return item

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items']

class ProductLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'product', 'created']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, attrs):
        user = self.context['request'].user
        if Address.objects.filter(user=user).count() >= 10:
            raise serializers.ValidationError("شما نمی‌توانید بیش از ۱۰ آدرس ثبت کنید.")
        return attrs
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)




























