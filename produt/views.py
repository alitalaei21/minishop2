from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from produt.models import Category, Product, OrderItem, Order, Baner, Cart
from produt.permissions import ModelViewSetsPermission, IsOwnerAuth
from produt.serializers import CategorySerializer, ProductSerializer, OrderItemSerializer, OrderSerializer, \
    BanerSerializer, CartSerializer, CartItemSerializer


# Create your views here.

class CategoryListApi(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ModelViewSetsPermission]
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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (ModelViewSetsPermission,)
class ProductCreateApi(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsOwnerAuth,)
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsOwnerAuth,)

class ProductDetailApiView(APIView):
    def get(self, request, pk):
        try:
            category = Product.objects.get(pk=pk)
            serializer = ProductSerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
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
    def get(self, request, pk):
        products = Product.objects.filter(special_sale=True)
        serializer_class = ProductSerializer(products,many=True)
        return Response(serializer_class.data)
class BanerviewListApi(generics.ListAPIView):
    queryset = Baner.objects.all()
    serializer_class = SpecialSaleView

class BanerCreateApi(generics.CreateAPIView):
    queryset = Baner.objects.all()
    serializer_class = BanerSerializer
    permission_classes = [IsOwnerAuth,]
class BanerDetailView(generics.DestroyAPIView):
    queryset = Baner.objects.all()
    serializer_class = BanerSerializer
    permission_classes = [IsOwnerAuth,]


class ProductFilterListApi(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        filtered_products = []

        for product in queryset:
            serializer = ProductSerializer(product)
            final_price = serializer.data['final_price']
            if final_price is not None:
                final_price = int(final_price)
                if min_price and final_price < int(min_price):
                    continue
                if max_price and final_price > int(max_price):
                    continue
                filtered_products.append(product)

        return filtered_products

class ProductCategoryFilterListApi(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_name = self.request.query_params.getlist('category_name')
        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)
        return queryset

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

















































































# in braye google authenticate hast

from django.views.generic import TemplateView
class Page(TemplateView):
    template_name = 'htmle.html'