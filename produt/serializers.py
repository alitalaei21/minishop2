from rest_framework import serializers
from django.db import models

from produt.models import Category, OrderItem, Order, Baner, CartItem, Cart, Like, Comment, \
    Address, Product, ProductVariant, SizeColor
from goldapi.goldapifun import get_gold_price
import logging

logger = logging.getLogger(__name__)

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'product', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_created_at(self, obj):
        return int(obj.created_at.timestamp() * 1000)

class SizeColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeColor
        fields = ['id', 'size', 'color']

class ProductVariantSerializer(serializers.ModelSerializer):
    size = serializers.IntegerField(source='size_color.size')
    color = serializers.CharField(source='size_color.color')
    raw_price = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'color', 'weight', 'stock', 'discount', 'raw_price', 'final_price', 'images']

    def create(self, validated_data):
        size_color_data = {
            'size': validated_data.pop('size_color')['size'],
            'color': validated_data.pop('size_color')['color']
        }
        images = validated_data.pop('images', [])
        size_color, created = SizeColor.objects.get_or_create(**size_color_data)
        variant = ProductVariant.objects.create(size_color=size_color, **validated_data)
        if images:
            variant.images = images
            variant.save()
        return variant

    def update(self, instance, validated_data):
        if 'size_color' in validated_data:
            size_color_data = {
                'size': validated_data.pop('size_color')['size'],
                'color': validated_data.pop('size_color')['color']
            }
            size_color, created = SizeColor.objects.get_or_create(**size_color_data)
            instance.size_color = size_color
        
        if 'images' in validated_data:
            instance.images = validated_data.pop('images')
        
        instance.weight = validated_data.get('weight', instance.weight)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.save()
        return instance

    def gold_api_price(self):
        try:
            response = get_gold_price()
            if response is None or response == 0:
                logger.warning("Could not get gold price, using default value")
                return 0
            return float(response)
        except Exception as e:
            logger.error(f"Error getting gold price in ProductVariantSerializer: {str(e)}")
            return 0
            
    def get_raw_price(self, obj):
        price_gold = self.gold_api_price()
        gold_price = (price_gold * obj.weight)
        # Get labor_wage from the parent product
        labor_wage = obj.product.labor_wage
        
        gold_price = gold_price + (gold_price * (labor_wage / 100))
        gold_price = gold_price + (gold_price * 0.09) #tax
        gold_price = gold_price + (gold_price * 0.07) #profit
        
        return int(gold_price)

    def get_final_price(self, obj):
        raw_price = self.get_raw_price(obj)
        if obj.discount > 0:
            discount_amount = raw_price * (obj.discount / 100)
            return int(raw_price - discount_amount)
        return raw_price

    def get_images(self, obj):
        request = self.context.get('request')
        if request:
            return [request.build_absolute_uri('/media/' + str(image)) for image in obj.images]
        return []

class ProductSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    variants = ProductVariantSerializer(many=True)
    comments = CommentSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    created_at = serializers.SerializerMethodField()
    uploaded_at = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'title',
                 'labor_wage', 'category', 'special_sale',
                 'tags', 'variants', 'comments', 'created_at', 'uploaded_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only prefetch related data when we're dealing with a queryset
        if isinstance(self.instance, models.QuerySet):
            self.instance = self.instance.prefetch_related(
                'variants',
                'variants__size_color',
                'comments',
                'comments__user'
            ).select_related('category')

    def get_created_at(self, obj):
        return int(obj.created_at.timestamp() * 1000)

    def get_uploaded_at(self, obj):
        return int(obj.uploaded_at.timestamp() * 1000)

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        product = Product.objects.create(**validated_data)

        for variant_data in variants_data:
            size_color_data = variant_data.pop('size_color')
            images = variant_data.pop('images', [])
            size_color, created = SizeColor.objects.get_or_create(**size_color_data)
            variant = ProductVariant.objects.create(
                product=product, 
                size_color=size_color, 
                **variant_data
            )
            if images:
                variant.images = images
                variant.save()

        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if variants_data is not None:
            # Keep track of updated variants to avoid deleting them
            updated_variants = []
            
            for variant_data in variants_data:
                variant_id = variant_data.get('id', None)
                if variant_id:
                    # Update existing variant
                    variant = instance.variants.get(id=variant_id)
                    size_color_data = variant_data.pop('size_color', None)
                    images = variant_data.pop('images', None)
                    
                    if size_color_data:
                        size_color, created = SizeColor.objects.get_or_create(**size_color_data)
                        variant.size_color = size_color
                    
                    for attr, value in variant_data.items():
                        setattr(variant, attr, value)
                    
                    if images is not None:
                        variant.images = images
                    
                    variant.save()
                    updated_variants.append(variant.id)
                else:
                    # Create new variant
                    size_color_data = variant_data.pop('size_color')
                    images = variant_data.pop('images', [])
                    size_color, created = SizeColor.objects.get_or_create(**size_color_data)
                    variant = ProductVariant.objects.create(
                        product=instance, 
                        size_color=size_color, 
                        **variant_data
                    )
                    if images:
                        variant.images = images
                        variant.save()
                    updated_variants.append(variant.id)
            
            # Delete variants that weren't updated
            instance.variants.exclude(id__in=updated_variants).delete()

        return instance

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
    order_items_detail = OrderItemSerializer(many=True, read_only=True, source='order_items')
    customer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_date', 'total_price', 'order_items_data', 'order_items_detail', 'status')
        read_only_fields = ('total_price', 'customer')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.instance, models.QuerySet):
            self.instance = self.instance.prefetch_related(
                'order_items__product'
            ).select_related('customer')

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items_data')
        validated_data['customer'] = self.context['request'].user
        order = Order.objects.create(**validated_data)
        
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        order.calculate_total_price()
        return order
class BanerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baner
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']
        read_only_fields = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.instance, models.QuerySet):
            self.instance = self.instance.prefetch_related(
                'items__product__variants__size_color',
            ).select_related('user')

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
