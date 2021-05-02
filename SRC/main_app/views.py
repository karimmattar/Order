from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import SafeJWTAuthentication
from .serializers import *
from .decorators import is_staff, is_normal


# Login view class
class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.clean()
        return Response(data, status=status.HTTP_200_OK)


# Register view class
class RegisterView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Products view class
class ProductView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (SafeJWTAuthentication,)
    serializer_class = ProductDetailSerializer
    serializer_class_many_true = ProductSerializer
    model_class = Product

    def get(self, request, id=None):
        if id is None:
            if 'currency' in request.GET.keys():
                success, products = self.model_class.objects.get_in_currency(str(request.GET.get('currency')).upper())
                if not success:
                    if products is None:
                        raise exceptions.NotAcceptable(_('Not acceptable'))
                    return Response(products, status=status.HTTP_409_CONFLICT)
            else:
                products = self.model_class.objects.all().order_by('-created_at')
            serializer = self.serializer_class_many_true(products, many=True)
            data = serializer.data
        else:
            try:
                product = self.model_class.objects.get(id=id)
            except ObjectDoesNotExist:
                raise exceptions.NotFound(_('Not found'))
            serializer = self.serializer_class(product)
            data = serializer.data
            if 'currency' in request.GET.keys():
                success, new_price = product.get_in_currency(str(request.GET.get('currency')).upper())
                if not success:
                    if new_price is None:
                        raise exceptions.NotAcceptable(_('Not acceptable'))
                    return Response(new_price, status=status.HTTP_409_CONFLICT)
                data['price'] = new_price
        return Response(data, status=status.HTTP_200_OK)

    @method_decorator([ensure_csrf_cookie, is_staff])
    def post(self, request):
        if 'price' not in request.data.keys():
            raise exceptions.APIException({'price': [_('This field is required.')]}, status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(price=request.data.get('price'))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @method_decorator([ensure_csrf_cookie, is_staff])
    def put(self, request, id):
        if 'price' not in request.data.keys():
            raise exceptions.APIException({'price': [_('This field is required.')]}, status.HTTP_400_BAD_REQUEST)
        try:
            product = self.model_class.objects.get(id=id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound(_('Not found'))
        serializer = self.serializer_class(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(price=request.data.get('price'))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @method_decorator([ensure_csrf_cookie, is_staff])
    def delete(self, request, id):
        try:
            product = self.model_class.objects.get(id=id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound(_('Not found'))
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Revenue view class
class RevenueView(APIView):
    permission_classes = (IsAdminUser,)
    authentication_classes = (SafeJWTAuthentication,)

    def get(self, request, id=None):
        if id is None:
            total_revenue = Order.objects.total_revenue()
        else:
            total_revenue = Product.objects.total_revenue(id)
        return Response(total_revenue, status=status.HTTP_200_OK)


# Order view class
class OrderView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SafeJWTAuthentication,)
    serializer_class = OrderSerializer
    model_class = Order

    @method_decorator(is_normal)
    def get(self, request, id=None):
        user = request.user
        if id is None:
            if 'currency' in request.GET.keys():
                success, orders = self.model_class.objects.get_in_currency(str(request.GET.get('currency')).upper(),
                                                                           user.id)
                if not success:
                    if orders is None:
                        raise exceptions.NotAcceptable(_('Not acceptable'))
                    return Response(orders, status=status.HTTP_409_CONFLICT)
            else:
                orders = self.model_class.objects.filter(buyer=user)
            serializer = self.serializer_class(orders, many=True)
            data = serializer.data
        else:
            try:
                order = self.model_class.objects.get(id=id)
            except ObjectDoesNotExist:
                raise exceptions.NotFound(_('Not found'))
            serializer = self.serializer_class(order)
            data = serializer.data
            if 'currency' in request.GET.keys():
                success, new_revenue = order.get_in_currency(str(request.GET.get('currency')).upper())
                if not success:
                    if new_revenue is None:
                        raise exceptions.NotAcceptable(_('Not acceptable'))
                    return Response(new_revenue, status=status.HTTP_409_CONFLICT)
                data['revenue'] = new_revenue
        return Response(data, status=status.HTTP_200_OK)

    @method_decorator([ensure_csrf_cookie, is_normal])
    def post(self, request):
        user = request.user
        if 'product' not in request.data.keys():
            raise exceptions.APIException({'product': [_('This field is required.')]}, status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=request.data.pop('product'))
        except ObjectDoesNotExist:
            raise exceptions.NotFound(_('Not found'))
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(buyer=user, product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
