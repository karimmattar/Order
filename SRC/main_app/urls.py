from django.urls import path

from . import views

urlpatterns = [
    # post login
    path('login/', views.LoginView.as_view(), name='login'),
    # post register
    path('register/', views.RegisterView.as_view(), name='register'),
    # get all products
    path('products', views.ProductView.as_view(), name='products'),
    # get product by id
    path('products/<int:id>', views.ProductView.as_view(), name='product'),
    # post product
    path('products/', views.ProductView.as_view(), name='products_create'),
    # put, delete product
    path('products/<int:id>/', views.ProductView.as_view(), name='products_u_d'),
    # get total revenues
    path('revenues', views.RevenueView.as_view(), name='revenues'),
    # get product revenues by id
    path('revenues/<int:id>', views.RevenueView.as_view(), name='revenue'),
    # get all orders
    path('orders', views.OrderView.as_view(), name='orders'),
    # get order by id
    path('orders/<int:id>', views.OrderView.as_view(), name='order'),
    # post order
    path('orders/', views.OrderView.as_view(), name='order_create'),
]
