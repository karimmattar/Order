from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Sum, F
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions
from rest_framework.authtoken.models import Token

from .models import Order, Product


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    # auto create user token
    if created:
        Token.objects.create(user=instance)


@receiver(pre_save, sender=Order)
def calculate_total_revenue(sender, instance, **kwargs):
    product = instance.product
    if not 0 < product.remain_in_stock >= instance.quantity:
        raise exceptions.NotAcceptable(_('Not acceptable'))
    instance.revenue = product.price * instance.quantity
