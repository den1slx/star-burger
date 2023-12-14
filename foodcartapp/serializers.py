from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.serializers import CharField, IntegerField, ListField, PrimaryKeyRelatedField
from rest_framework.serializers import ValidationError

from phonenumber_field.serializerfields import PhoneNumberField

from .models import Product, Order, OrderedProduct


class ProductSerializer(ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = IntegerField(min_value=1)

    class Meta:
        model = OrderedProduct
        fields = ['product', 'quantity']
        depth = 1


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
        updated_ordered_products = []
        updated_data = {
            'phonenumber': str(validated_data['phonenumber']),
            'firstname': validated_data['firstname'],
            'lastname': validated_data['lastname'],
            'address': validated_data['address'],
            'ordered_products': updated_ordered_products

        }
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )
        for ordered_product in validated_data['ordered_products']:
            product = ordered_product['product']
            OrderedProduct.objects.create(
                order=order,
                product=product,
                quantity=ordered_product['quantity'],
                price=ordered_product['quantity'] * product.price
            )

            updated_ordered_product = {
                'product': {
                    'name': product.name,
                    'price': product.price,
                    'id': product.id,
                },
                'quantity': ordered_product['quantity']
            }
            updated_ordered_products.append(updated_ordered_product)
        return updated_data
    
