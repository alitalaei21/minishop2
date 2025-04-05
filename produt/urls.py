from django.urls import path

from produt.views import Page, CategoryListApi, CategoryCreateApi, CategoryDetailView, CategoryDetailApiView, \
    ProductCreateApi, ProductDetailView, ProductListApi, ProductDetailApiView, OrderItemListCreateView, \
    OrderItemDetailView, OrderListCreateView, OrderDetailView

urlpatterns = [

    path('', Page.as_view(), name='page'),
    path('category/list/',CategoryListApi.as_view(), name='category-list'),
    path('category/create/',CategoryCreateApi.as_view(), name='category-create'),
    path('category/detale/<int:pk>/',CategoryDetailView.as_view(), name='category-detale'),
    path('category_pk/<int:pk>/',CategoryDetailApiView.as_view(), name='category-pk'),
    path('product/list/',ProductListApi.as_view(), name='product-list'),
    path('product/create/',ProductCreateApi.as_view(), name='product-create'),
    path('product/detale/',ProductDetailView.as_view(), name='product-detail'),
    path('product_pk/<int:pk>/',ProductDetailApiView.as_view(), name='product-pk'),
    path('order-items/', OrderItemListCreateView.as_view(), name='orderitem-list-create'),
    path('order-items/<int:pk>/', OrderItemDetailView.as_view(), name='orderitem-detail'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),


]