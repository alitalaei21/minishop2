from django.urls import path

from produt.models import CartItem
from produt.views import CategoryListApi, CategoryCreateApi, CategoryDetailView, CategoryDetailApiView, \
    ProductCreateApi, ProductDetailView, ProductListApi, ProductDetailApiView, OrderItemListCreateView, \
    OrderItemDetailView, OrderListCreateView, OrderDetailView, SpecialSaleView, BanerviewListApi, BanerCreateApi, \
    BanerDetailView, ProductFilterListApi, CartView, \
    ProductLikeToggleView, ProductCommentListCreateView, AddressApiView, AddressDetailView, ProductTag, GoldPriceView

urlpatterns = [
    path('category/list/',CategoryListApi.as_view(), name='category-list'),
    path('category/create/',CategoryCreateApi.as_view(), name='category-create'),
    path('category/detale/<int:pk>/',CategoryDetailView.as_view(), name='category-detale'),
    path('category_pk/<int:pk>/',CategoryDetailApiView.as_view(), name='category-pk'),
    path('product/create/',ProductCreateApi.as_view(), name='product-create'),
    path('product/detale/',ProductDetailView.as_view(), name='product-detail'),
    path('product_pk/<int:pk>/',ProductDetailApiView.as_view(), name='product-pk'),
    path('order-items/', OrderItemListCreateView.as_view(), name='orderitem-list-create'),
    path('order-items/<int:pk>/', OrderItemDetailView.as_view(), name='orderitem-detail'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('specialsale/',SpecialSaleView.as_view(), name='specialsale'),
    path('Baner/list/',BanerviewListApi.as_view(), name='banerview-list'),
    path('Baner/create/',BanerCreateApi.as_view(), name='banerview-list'),
    path('Baner/delete/',BanerDetailView.as_view(), name='banerview-list'),
    #todo restrict this to round values to be able to cache it
    path('products/',ProductFilterListApi.as_view(), name='filter-product-list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('products/<int:pk>/like/', ProductLikeToggleView.as_view(), name='product-like-toggle'),
    path('products/<int:product_id>/comments/', ProductCommentListCreateView.as_view(), name='product-comments'),
    path('addresses/', AddressApiView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('products/tag/', ProductTag.as_view(), name='product-list-by-tag'),
    path('au', GoldPriceView.as_view(), name='gold-price'),
]

