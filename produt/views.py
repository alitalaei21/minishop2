from django.core.cache import cache
from django.db.models import Q, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import logging

logger = logging.getLogger(__name__)

from produt.models import Category, OrderItem, Order, Baner, Cart, Like, Comment, Address, Product, ProductVariant
from produt.permissions import ModelViewSetsPermission, IsOwnerAuth
from produt.serializers import CategorySerializer, ProductSerializer, OrderItemSerializer, OrderSerializer, \
    BanerSerializer, CartSerializer, CartItemSerializer, CommentSerializer, AddressSerializer, ProductVariantSerializer

import base64
import json
import hashlib
import time
from datetime import datetime

class CustomPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        count = self.page.paginator.count
        total_pages = (count + self.page_size - 1) // self.page_size  # Ceiling division
        
        return Response({
            'count': count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': total_pages,
            'page_size': self.page_size,
            'current_page': self.page.number,
            'results': data
        })

class GoldPriceView(APIView):
    def encode_response(self, price):
        data = {
            "t": int(time.time()),  # timestamp
            "s": "xau_usd",  # symbol
            "v": float(price),  # value
            "h": hashlib.sha256(str(price).encode()).hexdigest()[:8],  # hash of price
            "n": datetime.utcnow().isoformat(),  # ISO timestamp
            "m": "live_market_data",  # metadata
            "r": 42 
        }
        
        json_data = json.dumps(data)
        encoded = base64.b64encode(json_data.encode()).decode()
        
        prefix = "XAUDATA"
        suffix = hashlib.sha256(encoded.encode()).hexdigest()[:12]
        
        return f"{prefix}.{encoded}.{suffix}"

    def get(self, request):
        try:
            from goldapi.goldapifun import get_gold_price
            price = get_gold_price()
            encoded_response = self.encode_response(price)
            return Response({
                "data": encoded_response,
                "format": "v1.xau.b64.meta",
                "length": len(encoded_response)
            })
        except Exception as e:
            logger.error(f"Error getting gold price: {str(e)}")
            return Response(
                {'error': 'Market data temporarily unavailable'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Create your views here.

class CategoryListApi(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ModelViewSetsPermission]
    pagination_class = None

class CategoryCreateApi(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated,]
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsOwnerAuth,)

class CategoryDetailApiView(APIView):
    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ProductListApi(generics.ListAPIView):
    queryset = Product.objects.all().prefetch_related('variants')
    serializer_class = ProductSerializer
    permission_classes = (ModelViewSetsPermission,)

class ProductCreateApi(generics.CreateAPIView):
    queryset = Product.objects.prefetch_related('variants')
    serializer_class = ProductSerializer
    permission_classes = (IsOwnerAuth,)
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.prefetch_related('variants')
    serializer_class = ProductSerializer
    permission_classes = (IsOwnerAuth,)

class ProductDetailApiView(APIView):
    def get(self, request, pk):
        try:
            category = Product.objects.prefetch_related('variants').get(product_id=pk)
            serializer = ProductSerializer(category, context={'request': request})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class OrderItemListCreateView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class SpecialSaleView(APIView):
    def get(self, request):
        # Get products that have at least one variant with special_sale=True
        products = Product.objects.filter(variants__special_sale=True).distinct().prefetch_related('variants')
        
        # Create a custom context that includes special_sale filter
        context = {'request': request, 'special_sale_only': True}
        serializer_class = ProductSerializer(products, many=True, context=context)
        return Response(serializer_class.data)
class BanerviewListApi(generics.ListAPIView):
    queryset = Baner.objects.all()
    serializer_class = BanerSerializer
    pagination_class = None

class BanerCreateApi(generics.CreateAPIView):
    queryset = Baner.objects.all()
    serializer_class = BanerSerializer
    permission_classes = [IsOwnerAuth,]
class BanerDetailView(generics.DestroyAPIView):
    queryset = Baner.objects.all()
    serializer_class = BanerSerializer
    permission_classes = [IsOwnerAuth,]


#todo Save product prices to Redis to avoid calculating them everytime
class ProductFilterListApi(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    MAX_SEARCH_LENGTH = 32  # Maximum allowed length for search text
    CACHE_TIMEOUT = 300  # 5 minutes cache timeout

    def get_cache_key(self, params):
        """Generate a unique cache key based on all filter parameters"""
        key_parts = []
        for param in sorted(params.items()):
            key_parts.append(f"{param[0]}:{param[1]}")
        return f"product_filter:{'|'.join(key_parts)}"

    def get_queryset(self):
        queryset = Product.objects.all().prefetch_related(
            Prefetch(
                'variants',
                queryset=ProductVariant.objects.all().order_by('id')
            )
        ).order_by('-product_id')
        
        # Get filter parameters
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        category_id = self.request.query_params.get('category_id')
        search = self.request.query_params.get('search')

        # Validate search text length
        if search and len(search) > self.MAX_SEARCH_LENGTH:
            return Product.objects.none()

        # Generate cache key based on all parameters
        cache_key = self.get_cache_key(self.request.query_params)
        
        # Try to get cached results
        cached_results = cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        # Apply search filter if search term exists
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(title__icontains=search)
            )

        # Apply category filter
        if category_id:
            try:
                category_id = int(category_id)
                queryset = queryset.filter(category__category_id=category_id)
            except (ValueError, TypeError):
                pass

        # If no price filters, cache and return the queryset
        if not min_price and not max_price:
            cache.set(cache_key, queryset, timeout=self.CACHE_TIMEOUT)
            return queryset

        # Apply price filtering
        try:
            min_price = float(min_price) if min_price else None
            max_price = float(max_price) if max_price else None
        except (ValueError, TypeError):
            cache.set(cache_key, queryset, timeout=self.CACHE_TIMEOUT)
            return queryset

        # Filter products based on variant prices
        filtered_products = []
        variant_serializer = ProductVariantSerializer(context={'request': self.request})
        
        for product in queryset:
            eligible_variants = []
            for variant in product.variants.all():
                variant_serializer.instance = variant
                final_price = variant_serializer.get_final_price(variant)
                if final_price is not None:
                    if ((min_price is None or final_price >= min_price) and 
                        (max_price is None or final_price <= max_price)):
                        eligible_variants.append(variant)
            
            if eligible_variants:
                product._prefetched_objects_cache = {
                    'variants': eligible_variants
                }
                filtered_products.append(product)

        # Cache the filtered results
        cache.set(cache_key, filtered_products, timeout=self.CACHE_TIMEOUT)
        return filtered_products

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cart,_ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    def post(self, request):
        cart,_ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data,context={'cart':cart})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "محصول به سبد اضافه شد"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, product=product)
        if not created:
            like.delete()
            return Response({'message': 'Unliked'}, status=status.HTTP_200_OK)
        return Response({'message': 'Liked'}, status=status.HTTP_201_CREATED)


class ProductCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Comment.objects.select_related('user').filter(product_id=product_id).order_by('-created_at')


    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        serializer.save(user=self.request.user, product_id=product_id)



class AddressApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class ProductTag(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        tag_name = request.query_params.get('tag')
        if tag_name:
            products = Product.objects.filter(tags__contains=[tag_name])
        else:
            products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
