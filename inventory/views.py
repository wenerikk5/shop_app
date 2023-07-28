from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib.postgres.aggregates import ArrayAgg
from mptt.forms import TreeNodeChoiceField

from django.db.models.functions import Cast
from django.db.models import IntegerField

from inventory import models, forms
from .logic import filter_product

# list range type items for products filtering
INPUT_TYPE_RANGE = [
    'screen_size',
    'threads',
    'frequency',
]


def home(request):
    return render(request, 'index.html')


def categories(request):
    data = models.Category.objects.filter(level=0).all()

    return render(request, 'category.html',
                  {'data': data})


def category(request, category_slug):
    data = get_object_or_404(models.Category, slug=category_slug).get_children()

    # print(TreeNodeChoiceField(queryset=models.Category.objects.all()))

    return render(request, 'category.html',
                  {'data': data})


def product_by_category(request, category_slug):
    category = get_object_or_404(models.Category, slug=category_slug)

    box_arguments = []
    range_arguments = []

    box_filter_dict = {}
    range_filter_dict = {}

    if request.method == 'POST' and (
        len(request.POST.get('box_attrs')) > 0
        or
        len(request.POST.get('range_attrs')) > 0
    ):
        if len(request.POST.get('box_attrs')) > 0:
            box_arguments = request.POST.get('box_attrs').split('&')
            for item in box_arguments:
                name, value = item.split(':')
                box_filter_dict.setdefault(name, []).append(value)
            print('box_filter_dict:', box_filter_dict)

        if len(request.POST.get('range_attrs')) > 0:
            range_arguments = request.POST.get('range_attrs').split('&')
            for item in range_arguments:
                name, value = item.split(':')
                name, limit = name.split('-')
                if limit == 'min':
                    range_filter_dict.setdefault(name, [None, None])[0] = int(value)
                else:
                    range_filter_dict.setdefault(name, [None, None])[1] = int(value)

            print('range_filter_dict', range_filter_dict)

        product_ids = filter_product(box_filter_dict, range_filter_dict, category) 

        products = models.Product.objects\
            .filter(id__in=product_ids)\
            .values(
                'id',
                'name',
                'slug',
                'category__name',
                'description',
            )
    else:
        products = models.Product.objects\
            .filter(category=category)\
            .values(
                'id',
                'name',
                'slug',
                'category__name',
                'description',
            )

    category_attrs = models.ProductAttribute.objects.filter(
        category=category)

    attr_values = models.ProductAttributeValue.objects\
        .filter(product_attribute__category__id=category.id)\
        .values(
            'value',
            'product_attribute__name',
            'product_attribute__category__id',
        )\
        .distinct()

    context = {
        'products': products,
        'category': category,
        'category_attrs': category_attrs,
        'attr_values': attr_values,
        'box_arguments': box_arguments,
        'range_filter_dict': range_filter_dict,
        'INPUT_TYPE_RANGE': INPUT_TYPE_RANGE,
    }

    return render(request, 'product_by_category.html', context)


def product_detail(request, product_slug):
    filter_arguments = []

    category_id = models.Product.objects.filter(slug=product_slug).first().category.id

    if request.GET:
        for value in request.GET.values():
            filter_arguments.append(value)

        product = models.ProductItem.objects\
            .filter(product__slug=product_slug)\
            .filter(product__category__id=category_id)\
            .filter(sku__in=filter_arguments)\
            .annotate(field_a=ArrayAgg(
                'sku')
            ).values(
                'id', 'sku', 'product__name', 'field_a',
            )
        if len(product) < 1:
            product = models.ProductItem.objects\
                .filter(product__slug=product_slug)\
                .filter(product__category__id=category_id)\
                .annotate(field_a=ArrayAgg(
                    'sku')
                ).values(
                    'id', 'sku', 'product__name', 'field_a',
                )
    else:
        product = models.ProductItem.objects\
            .filter(product__slug=product_slug)\
            .filter(product__category__id=category_id)\
            .annotate(field_a=ArrayAgg(
                'sku')
            ).values(
                'id', 'sku', 'product__name', 'field_a',
            )

    sku_values = models.Product.objects\
        .filter(slug=product_slug)\
        .filter(category__id=category_id)\
        .values('product__sku')

    context = {
        'product': product,
        'category': models.Category.objects.get(id=category_id),
        'sku_values': sku_values
    }
    return render(request, 'product_detail.html', context)


def add_product(request):
    form = forms.ProductForm(request.POST or None)

    if form.is_valid():
        cd = form.cleaned_data

        category = get_object_or_404(models.Category,
                                     id=cd.get('category_id'))
        product = models.Product.objects.create(
            name=cd.get('name_product'),
            slug=cd.get('slug_product'),
            description=cd.get('description'),
            category=category
        )
        product_attribute, _ = models.ProductAttribute.objects\
            .get_or_create(name=cd.get('name_attribute'), category=category)

        models.ProductAttributeValue.objects.create(
            product_attribute=product_attribute,
            value=cd.get('value_attribute')
        )

        models.ProductItem.objects.create(
            sku=cd.get('sku'),
            product=product
        )
        print('=====New Product is added')
        return redirect('inventory:categories')
    return render(request, 'add_product.html', {'form': form})

