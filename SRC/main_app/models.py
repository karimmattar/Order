import requests
import itertools

from django.conf import settings
from django.core.validators import validate_email
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager, ProductsAdministratorManager, SYMBOLS, OrderAdministratorManager


# Time stamp table
class TimeBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        verbose_name_plural = 'Time Stamp'


# User Table
# Inherits from AbstractBaseUser, PermissionsMixin, TimeBase
class User(AbstractBaseUser, PermissionsMixin, TimeBase):
    email = models.EmailField(validators=[validate_email], max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_terms_accepted = models.BooleanField(default=False)

    # other fields can be added here
    # like (first_name, last_name, phone_number, birth_date, gender)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['is_terms_accepted']

    class Meta:
        verbose_name_plural = 'Login Information'

    def __str__(self):
        return self.email


# Product table
class Product(TimeBase):
    name = models.CharField(max_length=120, null=False, blank=False)
    price = models.FloatField(blank=False, null=False, help_text='product default currency in EUR')
    quantity = models.IntegerField(null=False, blank=False)
    description = models.TextField()

    # other fields can be added here

    objects = ProductsAdministratorManager()

    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    @property
    def total_revenue(self):
        return self.purchased.all().aggregate(total_revenue=models.Sum('revenue'))

    @property
    def total_purchased_quantity(self):
        return self.purchased.all().aggregate(total_quantity=models.Sum('quantity'))

    # Returns remaining in stock
    @property
    def remain_in_stock(self):
        purchased = self.total_purchased_quantity['total_quantity']
        return self.quantity if purchased is None else self.quantity - purchased

    # Change currency
    def get_in_currency(self, currency):
        if str(currency).upper() in itertools.chain(*SYMBOLS):
            url = 'http://data.fixer.io/api/latest?access_key=%s&base=EUR&symbols=%s' \
                  % (settings.FIXER_ACCESS_KEY, str(currency).upper())
            res = requests.get(url)
            data = res.json()
            if not data['success']:
                return False, data
            return True, self.price * data['rates'][str(currency).upper()]
        return False, None


# Order table
class Order(TimeBase):
    buyer = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='purchased_products')
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='purchased')
    quantity = models.IntegerField(null=False, blank=False)
    revenue = models.FloatField(null=True, blank=True)

    # other fields can be added here

    objects = OrderAdministratorManager()

    class Meta:
        verbose_name_plural = 'Orders'

    def __str__(self):
        return '%s' % self.id

    # Change currency
    def get_in_currency(self, currency):
        if str(currency).upper() in itertools.chain(*SYMBOLS):
            url = 'http://data.fixer.io/api/latest?access_key=%s&base=EUR&symbols=%s' \
                  % (settings.FIXER_ACCESS_KEY, str(currency).upper())
            res = requests.get(url)
            data = res.json()
            if not data['success']:
                return False, data
            return True, self.revenue * data['rates'][str(currency).upper()]
        return False, None
