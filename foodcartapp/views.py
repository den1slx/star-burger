from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.http import JsonResponse
from django.templatetags.static import static


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
    error_422_response = get_error_422_response(data)
    if error_422_response:
        return Response(error_422_response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    phone = data['phonenumber']  # TODO add validator ?
    order = Order.objects.create(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=phone,
        address=data['address']
    )

    for ordered_product in data['products']:
        OrderedProduct.objects.create(
            order=order,
            product=Product.objects.get(id=ordered_product['product']),
            quantity=ordered_product['quantity'],
        )
    return Response(data)


def get_error_422_response(data):
    key_error_response = {
        "reason": "Be sure what you indicate all necessary keys",
        "phonenumber": "str",
        "firstname": "str",
        "lastname": "str",
        "address": "str",
        "products": [{"product": "int", "quantity": "int",},],
    }
    try:
        default_error_data = get_default_dict(
            ["phonenumber", "firstname", "lastname",
             "address", "products_list", "product_dict", "product_dict_values"], "correct")
        error_data = {}
        error_data.update(default_error_data)

        if not isinstance(data['phonenumber'], str):
            error_data.update({"phonenumber": "not correct"})
        if not isinstance(data['firstname'], str):
            error_data["firstname"] = "not correct: available type str"
        if not isinstance(data["lastname"], str):
            error_data["lastname"] = "not correct: available type str"
        if not isinstance(data["address"], str):
            error_data["address"] = "not correct: available type str"
        if not isinstance(data["products"], list):
            error_data["products_list"] = "not correct: available type list"
            error_data.update({
                "products_list": "not correct: available type list",
                "product_dict": None,
                "product_dict_values": None
            })
        elif not data['products']:
            error_data.update({
                "products_list": "not correct: null and none not available",
                "product_dict": None,
                "product_dict_values": None
            })
        else:
            for product in data["products"]:
                if not isinstance(product, dict):
                    error_data.update({
                        "product_dict": "not correct: be sure all values of list is dict",
                        "product_dict_values": None,
                    })
                elif not product:
                    error_data.update({
                        "product_dict": "not correct: null and none not available",
                        "product_dict_values": None
                    })
                else:
                    error_text = ''
                    if not isinstance(product["quantity"], int):
                        error_text += "not correct: available type int "
                    if not isinstance(product["product"], int):
                        error_text += "not correct: available type int "
                    if error_text:
                        error_data.update({"product_dict_values": error_text})
    except KeyError:
        return key_error_response

    if error_data == default_error_data:
        return
    else:
        return error_data


def get_default_dict(keys, default_value):
    default_dict = {}
    for key in keys:
        default_dict.update({key: default_value})

    return default_dict
