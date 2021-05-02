import json

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from ..models import Product, Order
from ..serializers import OrderSerializer, ProductSerializer, ProductDetailSerializer
from ..utils import generate_access_token

# initialize the APIClient app
client = Client()

User = get_user_model()


# Login test cases
class LoginViewsTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            email='user@user.com',
            is_terms_accepted=True
        )
        user.set_password('user')
        user.save()

        self.valid_data = {
            'email': 'user@user.com',
            'password': 'user'
        }

        self.invalid_data = {
            'email': 'user2345@user.com',
            'password': 'user'
        }

    def test_valid_data(self):
        response = client.post('/login/', data=json.dumps(self.valid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_data(self):
        response = client.post('/login/', data=json.dumps(self.invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# Register test cases
class RegisterViewsTest(TestCase):
    def setUp(self):
        self.init_data = {
            'email': 'register@register.com',
            'is_terms_accepted': True,
            'password1': 'register',
            'password2': 'register'
        }

        User.objects.create(
            email='exist@exist.com', is_terms_accepted=True
        )

        self.invalid_data = {
            'email': 'exist@exist.com',
            'is_terms_accepted': True,
            'password1': 'register',
            'password2': 'register'
        }

        self.invalid_data_terms = {
            'email': 'register@register.com',
            'is_terms_accepted': False,
            'password1': 'register',
            'password2': 'register'
        }

        self.invalid_data_password = {
            'email': 'register@register.com',
            'is_terms_accepted': True,
            'password1': 'register',
            'password2': 'register1'
        }

    def test_register(self):
        response = client.post('/register/', data=json.dumps(self.init_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_exist_email_register(self):
        response = client.post('/register/', data=json.dumps(self.invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_terms_accepted_register(self):
        response = client.post('/register/', data=json.dumps(self.invalid_data_terms), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_match_password_register(self):
        response = client.post('/register/', data=json.dumps(self.invalid_data_password),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# Product test cases
class ProductViewTest(TestCase):
    def setUp(self):
        Product.objects.create(
            name='product name', price=120, quantity=1000, description='No content'
        )

        self.init_data = {
            'name': 'test create product',
            'price': 12.25,
            'quantity': 10,
            'description': 'No content'
        }

    def test_get_all_products(self):
        response = client.get('/products', content_type='application/json')
        products = Product.objects.all().order_by('-created_at')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_product_by_id(self):
        product, created = Product.objects.get_or_create(
            name='product name', price=120, quantity=1000, description='No content'
        )
        response = client.get(f'/products/{product.id}', content_type='application/json')
        serializer = ProductDetailSerializer(product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_product(self):
        user = User.objects.create(
            email='admin@admin.com', is_terms_accepted=True, is_staff=True
        )
        access_token = generate_access_token(user)
        response = client.post('/products/', data=json.dumps(self.init_data),
                               content_type='application/json', Authorization='Token %s' % access_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_product(self):
        product, created = Product.objects.get_or_create(
            name='product name', price=120, quantity=1000, description='No content'
        )
        user = User.objects.create(
            email='admin@admin.com', is_terms_accepted=True, is_staff=True
        )
        access_token = generate_access_token(user)
        response = client.put('/products/%s/' % product.id, data=json.dumps(self.init_data),
                              content_type='application/json', Authorization='Token %s' % access_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_product(self):
        product, created = Product.objects.get_or_create(
            name='product name', price=120, quantity=1000, description='No content'
        )
        user = User.objects.create(
            email='admin@admin.com', is_terms_accepted=True, is_staff=True
        )
        access_token = generate_access_token(user)
        response = client.delete('/products/%s/' % product.id,
                                 content_type='application/json', Authorization='Token %s' % access_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# Admin revenue test cases
class RevenueViewTest(TestCase):
    def setUp(self):
        Product.objects.create(
            name='product name', price=120, quantity=1000, description='No content'
        )

    def test_total_products_revenue(self):
        user = User.objects.create(
            email='admin@admin.com', is_terms_accepted=True, is_staff=True
        )
        access_token = generate_access_token(user)
        response = client.delete('/revenues', content_type='application/json', Authorization='Token %s' % access_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_revenue(self):
        user = User.objects.create(
            email='admin@admin.com', is_terms_accepted=True, is_staff=True
        )
        product, created = Product.objects.get_or_create(
            name='product name', price=120, quantity=1000, description='No content'
        )
        access_token = generate_access_token(user)
        response = client.delete('/revenues/%s' % product.id, content_type='application/json',
                                 Authorization='Token %s' % access_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# Customer orders test cases
class OrderViewTest(TestCase):
    def setUp(self):
        User.objects.create(
            email='admin@admin.com', is_terms_accepted=True
        )

        Product.objects.create(
            name='product name', price=120, quantity=1000, description='No content'
        )

    def test_create_order(self):
        user = User.objects.get(email='admin@admin.com')
        product, created = Product.objects.get_or_create(
            name='product name', price=120, quantity=1000, description='No content'
        )
        access_token = generate_access_token(user)
        data = {
            'product': product.id,
            'quantity': 2
        }
        response = client.post('orders/', content_type='application/json', data=json.dumps(data),
                               Authorization='Token %s' % access_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_user_orders(self):
        user = User.objects.get(email='admin@admin.com')
        access_token = generate_access_token(user)
        response = client.get('orders', content_type='application/json',
                              Authorization='Token %s' % access_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
