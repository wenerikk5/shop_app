from django import template
from django.conf import settings
from pathlib import Path


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
        return ''
