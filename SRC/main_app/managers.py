import itertools
import requests

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.db import models

from rest_framework import exceptions

# check all available symbols
# http://data.fixer.io/api/latest?access_key=API_KEY
SYMBOLS = (
    ('AED', 'AED'), ('AFN', 'AFN'), ('ALL', 'ALL'), ('AMD', 'AMD'), ('ANG', 'ANG'), ('AOA', 'AOA'), ('ARS', 'ARS'),
    ('AUD', 'AUD'), ('AWG', 'AWG'), ('AZN', 'AZN'), ('BAM', 'BAM'), ('BBD', 'BBD'), ('BDT', 'BDT'), ('BGN', 'BGN'),
    ('BHD', 'BHD'), ('BIF', 'BIF'), ('BMD', 'BMD'), ('BND', 'BND'), ('BOB', 'BOB'), ('BRL', 'BRL'), ('BSD', 'BSD'),
    ('BTC', 'BTC'), ('BTN', 'BTN'), ('BWP', 'BWP'), ('BYN', 'BYN'), ('BYR', 'BYR'), ('BZD', 'BZD'), ('CAD', 'CAD'),
    ('CDF', 'CDF'), ('CHF', 'CHF'), ('CLF', 'CLF'), ('CLP', 'CLP'), ('CNY', 'CNY'), ('COP', 'COP'), ('CRC', 'CRC'),
    ('CUC', 'CUC'), ('CUP', 'CUP'), ('CVE', 'CVE'), ('CZK', 'CZK'), ('DJF', 'DJF'), ('DKK', 'DKK'), ('DOP', 'DOP'),
    ('DZD', 'DZD'), ('EGP', 'EGP'), ('ERN', 'ERN'), ('ETB', 'ETB'), ('EUR', 'EUR'), ('FJD', 'FJD'), ('FKP', 'FKP'),
    ('GBP', 'GBP'), ('GEL', 'GEL'), ('GGP', 'GGP'), ('GHS', 'GHS'), ('GIP', 'GIP'), ('GMD', 'GMD'), ('GNF', 'GNF'),
    ('GTQ', 'GTQ'), ('GYD', 'GYD'), ('HKD', 'HKD'), ('HNL', 'HNL'), ('HRK', 'HRK'), ('HTG', 'HTG'), ('HUF', 'HUF'),
    ('IDR', 'IDR'), ('ILS', 'ILS'), ('IMP', 'IMP'), ('INR', 'INR'), ('IQD', 'IQD'), ('IRR', 'IRR'), ('ISK', 'ISK'),
    ('JEP', 'JEP'), ('JMD', 'JMD'), ('JOD', 'JOD'), ('JPY', 'JPY'), ('KES', 'KES'), ('KGS', 'KGS'), ('KHR', 'KHR'),
    ('KMF', 'KMF'), ('KPW', 'KPW'), ('KRW', 'KRW'), ('KWD', 'KWD'), ('KYD', 'KYD'), ('KZT', 'KZT'), ('LAK', 'LAK'),
    ('LBP', 'LBP'), ('LKR', 'LKR'), ('LRD', 'LRD'), ('LSL', 'LSL'), ('LTL', 'LTL'), ('LVL', 'LVL'), ('LYD', 'LYD'),
    ('MAD', 'MAD'), ('MDL', 'MDL'), ('MGA', 'MGA'), ('MKD', 'MKD'), ('MMK', 'MMK'), ('MNT', 'MNT'), ('MOP', 'MOP'),
    ('MRO', 'MRO'), ('MUR', 'MUR'), ('MVR', 'MVR'), ('MWK', 'MWK'), ('MXN', 'MXN'), ('MYR', 'MYR'), ('MZN', 'MZN'),
    ('NAD', 'NAD'), ('NGN', 'NGN'), ('NIO', 'NIO'), ('NOK', 'NOK'), ('NPR', 'NPR'), ('NZD', 'NZD'), ('OMR', 'OMR'),
    ('PAB', 'PAB'), ('PEN', 'PEN'), ('PGK', 'PGK'), ('PHP', 'PHP'), ('PKR', 'PKR'), ('PLN', 'PLN'), ('PYG', 'PYG'),
    ('QAR', 'QAR'), ('RON', 'RON'), ('RSD', 'RSD'), ('RUB', 'RUB'), ('RWF', 'RWF'), ('SAR', 'SAR'), ('SBD', 'SBD'),
    ('SCR', 'SCR'), ('SDG', 'SDG'), ('SEK', 'SEK'), ('SGD', 'SGD'), ('SHP', 'SHP'), ('SLL', 'SLL'), ('SOS', 'SOS'),
    ('SRD', 'SRD'), ('STD', 'STD'), ('SVC', 'SVC'), ('SYP', 'SYP'), ('SZL', 'SZL'), ('THB', 'THB'), ('TJS', 'TJS'),
    ('TMT', 'TMT'), ('TND', 'TND'), ('TOP', 'TOP'), ('TRY', 'TRY'), ('TTD', 'TTD'), ('TWD', 'TWD'), ('TZS', 'TZS'),
    ('UAH', 'UAH'), ('UGX', 'UGX'), ('USD', 'USD'), ('UYU', 'UYU'), ('UZS', 'UZS'), ('VEF', 'VEF'), ('VND', 'VND'),
    ('VUV', 'VUV'), ('WST', 'WST'), ('XAF', 'XAF'), ('XAG', 'XAG'), ('XAU', 'XAU'), ('XCD', 'XCD'), ('XDR', 'XDR'),
    ('XOF', 'XOF'), ('XPF', 'XPF'), ('YER', 'YER'), ('ZAR', 'ZAR'), ('ZMK', 'ZMK'), ('ZMW', 'ZMW'), ('ZWL', 'ZWL')
)


# Create super user manager
class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, is_terms_accepted, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError({'email': _('The Email must be set')})
        if not is_terms_accepted or is_terms_accepted == False:
            raise ValueError({'terms&conditions': _('Please accept our terms')})
        email = self.normalize_email(email)
        user = self.model(email=email, is_terms_accepted=is_terms_accepted, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_terms_accepted', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if extra_fields.get('is_terms_accepted') is not True:
            raise ValueError(_('Superuser must have is_terms_accepted=True.'))
        return self.create_user(email, password, **extra_fields)


# Product manager
class ProductsAdministratorManager(models.Manager):
    # Return total product revenue if product is exist
    # else
    # raise object not found
    def total_revenue(self, product_id):
        try:
            total = super(ProductsAdministratorManager, self).get_queryset().get(
                id=product_id).purchased.all().aggregate(total_revenue=models.Sum('revenue'))
        except ObjectDoesNotExist:
            raise exceptions.NotFound(_('Not found'))
        return total

    # Return all products in different currency
    def get_in_currency(self, currency):
        if str(currency).upper() in itertools.chain(*SYMBOLS):
            url = 'http://data.fixer.io/api/latest?access_key=%s' % settings.FIXER_ACCESS_KEY
            res = requests.get(url)
            data = res.json()
            if not data['success']:
                return False, data
            return True, super(ProductsAdministratorManager, self).get_queryset().all().annotate(
                new_price=models.F('price') * data['rates'][str(currency).upper()])
        return False, None


# Order manager
class OrderAdministratorManager(models.Manager):
    # Return total orders revenue for all products
    def total_revenue(self):
        total = super(OrderAdministratorManager, self).get_queryset().all().aggregate(
            total_revenue=models.Sum('revenue'))
        return total

    # Return revenue to filtered orders by user in different currency
    def get_in_currency(self, currency, user_id):
        if str(currency).upper() in itertools.chain(*SYMBOLS):
            url = 'http://data.fixer.io/api/latest?access_key=%s' % settings.FIXER_ACCESS_KEY
            res = requests.get(url)
            data = res.json()
            if not data['success']:
                return False, data
            return True, super(OrderAdministratorManager, self).get_queryset().filter(buyer__id=user_id).annotate(
                new_revenue=models.F('revenue') * data['rates'][str(currency).upper()])
        return False, None
