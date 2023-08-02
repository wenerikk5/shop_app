from django import template
from django.conf import settings
from pathlib import Path
from inventory import models


register = template.Library()


@register.filter
def addstr(arg1, arg2):
    """Concatenate arg1 and arg2"""
    return f'{arg1}:{arg2}'


@register.filter
def from_dict(d, key):
    return d.get(key)


@register.filter
def from_list(d, key):
    try:
        val = d[key]
    except:
        val = []
    return val


@register.filter
def get_url(media_path):
    if media_path:
        return '/media/' + media_path
    else:
        return '/media/no_image.png'


@register.filter
def delimiter(num):
    return f'{num:,}'


@register.filter
def get_product_image(product_item_id):
    media = models.ProductMedia.objects.get(product_item=product_item_id)
    if media:
        return media.img_url.url
    return '/media/no_image.png'


@register.filter
def get_product_image_thumb(product_item_id):
    media = models.ProductMedia.objects.get(product_item=product_item_id)
    if media:
        return media.img_url
    return '/media/no_image.png'
