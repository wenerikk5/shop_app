from django import template
from django.urls import reverse
from django.shortcuts import get_object_or_404
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
def get_image_by_product_slug(product_slug):
    product_item_id = get_product_first(product_slug).id
    return get_image_by_product_item_id(product_item_id)


@register.filter
def get_image_by_product_item_id(product_item_id):
    product_media = models.ProductMedia.objects\
        .filter(product_item=product_item_id)
    if product_media:
        return product_media[0].img_url.url
    else:
        return '/media/no_image.png'


@register.filter
def delimiter(num):
    if num:
        return f'{num:,}'
    return


@register.filter
def get_product_image_thumb(product_item_id):
    media = models.ProductMedia.objects.filter(product_item=product_item_id)
    if media:
        return media[0].img_url

    return 'no_image.png'


@register.filter
def get_product_url(product_id):
    product = get_object_or_404(models.Product, id=product_id)
    return reverse("inventory:product_detail",
                   kwargs={"product_slug": product.slug})


@register.filter
def get_product_item_url(product_item_id):
    product_item = get_object_or_404(models.ProductItem, id=product_item_id)
    slug = models.ProductItem.objects\
        .filter(id=product_item.id)\
        .values('product__slug')
    return reverse("inventory:product_detail",
                   kwargs={"product_slug": slug[0].get('product__slug')})


@register.filter
def get_product_first(product_slug):
    """
    Return ProductItem with a lowest price.
    """
    product = models.ProductItem.objects\
        .filter(product__slug=product_slug)\
        .order_by('price')\
        .first()
    return product


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})
