from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.serializers import CharField, IntegerField, ListField
from rest_framework.serializers import ValidationError

from phonenumber_field.serializerfields import PhoneNumberField

from .models import Product, Order, OrderedProduct


class ProductSerializer(ModelSerializer):
    product = IntegerField(min_value=1)
    quantity = IntegerField(min_value=1)

    def validate_product(self, value):
        products = Product.objects.all()
        product = products.filter(id=value)
        if not product:
            raise ValidationError(f'Product {value} does not exist')
        return value

    class Meta:
        model = OrderedProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    phonenumber = PhoneNumberField(region='RU')
    firstname = CharField()
    lastname = CharField()
    address = CharField()
    ordered_products = ListField(child=ProductSerializer(), allow_empty=False)

    class Meta:
        model = Order
        fields = ['phonenumber', 'firstname', 'lastname', 'address', 'ordered_products']

    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )
        for ordered_product in validated_data['ordered_products']:
            product = Product.objects.get(id=ordered_product['product'])
            OrderedProduct.objects.create(
                order=order,
                product=product,
                quantity=ordered_product['quantity'],
                price=ordered_product['quantity'] * product.price
            )
        return order

