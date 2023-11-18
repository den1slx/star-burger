from geopy.geocoders import Yandex
from geopy import distance

from django import template
from django.utils import timezone
from django.conf import settings

from foodcartapp.models import GeoData, WrongGeoData


register = template.Library()
api_key = settings.YANDEX_TOKEN
yandex_geolocator = Yandex(user_agent='restaurateur', api_key=api_key)


@register.filter(name='get_distance')
def get_distance(value, arg):
    restaurant = GeoData.objects.filter(address=value)
    client = GeoData.objects.filter(address=arg)
    if restaurant:
        restaurant = restaurant.first()
        restaurant = (restaurant.lat, restaurant.lng)
    else:
        restaurant = update_geodata(value)

    if client:
        client = client.first()
        client = (client.lat, client.lng)
    else:
        client = update_geodata(arg)
    if not client or not restaurant:
        return 'Расстояние не определено'
    return f'До вас {distance.distance(client, restaurant).km} км'


@register.filter(name='update_geodata')
def update_geodata(address, return_data='coords'):
    if WrongGeoData.objects.filter(address=address):
        return ''
    try:
        place = yandex_geolocator.geocode(address, exactly_one=True)
        location = place.address
        now = timezone.now()
        lat, lng = place.latitude, place.longitude

    except AttributeError:
        place, boolean = WrongGeoData.objects.get_or_create(address=address)
        return ''

    place, boolean = GeoData.objects.get_or_create(address=address)
    update_place(place, lng, lat, now, location)
    if return_data == 'coords':
        return lat, lng
    elif return_data == 'address':
        return address
    else:
        return ''


@register.filter(name='add_context')
def add_context(value, arg):
    return value, arg


def update_place(place, lng, lat, updated_at, address):
    place.lng = lng
    place.lat = lat
    place.updated_at = updated_at
    place.geolocate = address
    place.save()
    return

