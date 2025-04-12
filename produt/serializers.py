from rest_framework import serializers

from produt.models import Product, Category, OrderItem, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name','image','price','description','category',)
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

