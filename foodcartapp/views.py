from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.serializers import CharField, IntegerField, ListField
from rest_framework.serializers import ValidationError

from phonenumber_field.validators import validate_international_phonenumber

from django.http import JsonResponse
from django.templatetags.static import static
from django.core.validators import MinValueValidator, DecimalValidator


from .models import Product, Order, OrderedProduct


@api_view(['GET'])
def banners_list_api(request):
    # FIXME move data to db?
    # return JsonResponse([
    #     {
    #         'title': 'Burger',
    #         'src': static('burger.jpg'),
    #         'text': 'Tasty Burger at your door step',
    #     },
    #     {
    #         'title': 'Spices',
    #         'src': static('food.jpg'),
    #         'text': 'All Cuisines',
    #     },
    #     {
    #         'title': 'New York',
    #         'src': static('tasty.jpg'),
    #         'text': 'Food is incomplete without a tasty dessert',
    #     }
    # ], safe=False, json_dumps_params={
    #     'ensure_ascii': False,
    #     'indent': 4,
    # })
    return Response([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ])


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    # return JsonResponse(dumped_products, safe=False, json_dumps_params={
    #     'ensure_ascii': False,
    #     'indent': 4,
    # })
    return Response(dumped_products)


@api_view(['POST'])
def register_order(request):
    data = request.data
    serializor = OrderSerializer(data=data)
    serializor.is_valid(raise_exception=True)
    data = serializor.validated_data

    phone = data['phonenumber']
    order = Order.objects.create(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=phone,
        address=data['address']
    )

    for ordered_product in data['products']:
        product = Product.objects.get(id=ordered_product['product'])
        OrderedProduct.objects.create(
            order=order,
            product=product,
            quantity=ordered_product['quantity'],
            price=ordered_product['quantity'] * product.price
        )
    return Response(data)


class ProductSerializer(Serializer):
    product = IntegerField()
    quantity = IntegerField()

    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError('Not a valid value: quantity <= 0')
        return value

    def validate_product(self, value):
        products = Product.objects.all()
        if value <= 0:
            raise ValidationError('Not a valid value: product <= 0')
        if not products.filter(id=value):
            raise ValidationError(f'Product {value} does not exist')
        return value


class OrderSerializer(Serializer):
    phonenumber = CharField()
    firstname = CharField()
    lastname = CharField()
    address = CharField()
    products = ListField(child=ProductSerializer(), allow_empty=False)

    def validate_phonenumber(self, value):
        if value[0] == '8':
            value = value.replace("8", "+7", 1)
        validate_international_phonenumber(value)
        return value
