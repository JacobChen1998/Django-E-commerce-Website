

from django.urls import path
from . import views





urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<int:category_id>/', views.product_list, name='product_list_by_category'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='checkout'),
]