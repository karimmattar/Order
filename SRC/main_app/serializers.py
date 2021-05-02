from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, exceptions, status

from .utils import generate_access_token, generate_refresh_token
from .models import Product, Order


# User login serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_null=False)
    password = serializers.CharField(required=True, allow_null=False)

    User = get_user_model()

    def clean(self):
        email = self.validated_data['email']
        pwd = self.validated_data['password']
        try:
            user = self.User.objects.get(email=email)
            if not user.check_password(pwd):
                raise exceptions.AuthenticationFailed(_('Wrong password'))
            access_token = generate_access_token(user)
            token_version = user.auth_token.key
            refresh_token = generate_refresh_token(user, token_version)
            return {
                'access_token': access_token, 'refresh_token': refresh_token, 'id': user.id, 'is_staff': user.is_staff
            }
        except ObjectDoesNotExist:
            raise exceptions.NotFound(_('Not found'))


# User creation serializer
class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(required=True, allow_null=False, write_only=True)
    password2 = serializers.CharField(required=True, allow_null=False, write_only=True)
    is_terms_accepted = serializers.BooleanField(required=True, write_only=True)
    email = serializers.EmailField(required=True, allow_null=False)

    class Meta:
        model = get_user_model()
        fields = [
            'email', 'is_terms_accepted', 'password1', 'password2'
        ]

    def check_terms_is_accepted(self):
        # Check if terms are accepted
        if not self.validated_data['is_terms_accepted']:
            raise exceptions.AuthenticationFailed(_('Accept terms and conditions'))
        return True

    def check_email_exist(self):
        if self.Meta.model.objects.filter(email=self.validated_data['email']).exists():
            raise exceptions.AuthenticationFailed(_('Already exist'))
        return self.validated_data['email']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.validated_data['password1']
        password2 = self.validated_data['password2']
        if password1 and password2 and password1 != password2:
            raise exceptions.AuthenticationFailed(_("Passwords doesn't match"))
        return password2
    
    def save(self, **kwargs):
        terms = self.check_terms_is_accepted()
        password = self.clean_password2()
        email = self.check_email_exist()
        user = self.Meta.model(
            email=email,
            is_terms_accepted=terms
        )
        user.set_password(password)
        user.save()
        return user


# Product serializer on many=True
class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price'
        ]

    # check if obj has new price(in different currency) then return it
    def get_price(self, obj):
        if hasattr(obj, 'new_price'):
            return obj.new_price
        return obj.price


# Product serializer on CRUD by ID
class ProductDetailSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'created_at'
        ]

    def get_price(self, obj):
        # check if obj has new price(in different currency) then return it
        if hasattr(obj, 'new_price'):
            return obj.new_price
        return obj.price


# Order serializer on CRUD, many=True
class OrderSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)
    revenue = serializers.SerializerMethodField()
    buyer = serializers.ReadOnlyField(source='Order.buyer.id')

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'created_at'
        ]

    # check if obj has new revenue(in different currency) then return it
    def get_revenue(self, obj):
        if hasattr(obj, 'new_revenue'):
            return obj.new_revenue
        return obj.revenue
