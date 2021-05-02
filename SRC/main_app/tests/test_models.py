from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Product, Order

User = get_user_model()


# User create test case
class UserTest(TestCase):
    def setUp(self):
        user1 = User.objects.create(
            email='test1@test1.com', is_terms_accepted=True
        )
        user1.set_password('test1')
        user1.save()
        user2 = User.objects.create(
            email='test2@test2.com', is_terms_accepted=True
        )
        user2.set_password('test2')
        user2.save()

    def test_user(self):
        user1 = User.objects.get(email='test1@test1.com')
        user2 = User.objects.get(email='test2@test2.com')
        self.assertEqual(user1.is_terms_accepted, True)
        self.assertEqual(user2.is_terms_accepted, True)


# Product create test case
class ProductTest(TestCase):
    def setUp(self):
        Product.objects.create(
            name='unique_name_for_test', price=10.75, quantity=20, description='No details'
        )

    def test_product(self):
        product = Product.objects.get(name='unique_name_for_test')
        self.assertEqual(product.total_revenue['total_revenue'], None)
        self.assertEqual(product.total_purchased_quantity['total_quantity'], None)
        self.assertEqual(product.remain_in_stock, product.quantity)


# Order create test case
class OrderTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            email='user@user.com', is_terms_accepted=True
        )
        user.set_password('user')
        user.save()
        product = Product.objects.create(
            name='unique_name_for_order', price=10.75, quantity=20, description='No details'
        )
        Order.objects.create(
            buyer=user, product=product, quantity=10
        )

    def test_order(self):
        user = User.objects.get(email='user@user.com')
        product = Product.objects.get(name='unique_name_for_order')
        order = Order.objects.get(buyer=user, product=product)
        success, in_egp_currency = order.get_in_currency('EGP')
        self.assertEqual(in_egp_currency, (order.revenue * 18.823))
