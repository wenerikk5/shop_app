from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib.postgres.aggregates import ArrayAgg
from mptt.forms import TreeNodeChoiceField

from django.db.models.functions import Cast
from django.db.models import IntegerField

from inventory import models, forms

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

        attr_names = list(box_filter_dict.keys()) + list(range_filter_dict.keys())
        print('attr_names', attr_names)

        attribute_values = models.ProductAttributeValue.objects\
            .filter(product_attribute__category=category)\
            .filter(product_attribute__name__in=attr_names)

        for name, values in box_filter_dict.items():
            attribute_values = attribute_values\
                .filter(product_attribute__name=name,
                        value__in=values)\

        attribute_values = attribute_values.values('product_item__product__id')

        product_ids = set([x.get('product_item__product__id') for x in attribute_values])

        for name, values in range_filter_dict.items():
            attribute_values = models.ProductAttributeValue.objects\
                .filter(product_item__product__id__in=product_ids)\
                .filter(product_attribute__name=name)
            if values[0] and values[1]:
                attribute_values = attribute_values\
                    .filter(
                        value_number__gte=values[0],
                        value_number__lte=values[1]
                    )
            elif values[0]:
                attribute_values = attribute_values\
                    .filter(value_number__gte=values[0])

            else:
                attribute_values = attribute_values\
                    .filter(value_number__lte=values[1])

            attribute_values = attribute_values.values(
                'product_item__product__id'
            )

            ids = set([x.get('product_item__product__id') for x in attribute_values])
            print('product_ids:', product_ids)
            print('ids:', ids)
            product_ids = product_ids.intersection(ids)

        print('product_ids:', product_ids)





        # products = models.Product.objects.filter(category=category)

        # for name in box_filter_dict.keys():
        #     products = products\
        #         .filter(
        #             category__product_attribute__name=name,
        #             product__attribute_value__value__in=box_filter_dict[name]
        #         )
        # products = products.values('id')

        # # Filter by range attributes. Find attribute values, filter by 
        # # attribute name and convert to Integer for filter with gte and lte.
        # # Collect attribute values id's.
        # product_ids = set([x.get('id') for x in products])
        # first = True

        # for name in range_filter_dict.keys():
        #     attribute_values = models.ProductAttributeValue.objects\
        #         .filter(product_item__product__id__in=product_ids)\
        #         .filter(product_attribute__name=name)\
        #         .annotate(number=Cast('value',
        #                               output_field=IntegerField()))

        #     if range_filter_dict[name][0] and range_filter_dict[name][1]:
        #         attribute_values = attribute_values\
        #             .filter(
        #                 number__gte=range_filter_dict[name][0],
        #                 number__lte=range_filter_dict[name][1]
        #             ).values('product_item__product__id')
        #     elif range_filter_dict[name][0]:
        #         attribute_values = attribute_values\
        #             .filter(number__gte=range_filter_dict[name][0])\
        #             .values('product_item__product__id')
        #     else:
        #         attribute_values = attribute_values\
        #             .filter(number__lte=range_filter_dict[name][1])\
        #             .values('product_item__product__id')

        #     ids = set([x.get('product_item__product__id') for x in attribute_values])
        #     print('product_ids:', product_ids)
        #     print('ids:', ids)
        #     product_ids = product_ids.intersection(ids)

        # print('product_ids:', product_ids)

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
        'category_name': category.name,
        'category_attrs': category_attrs,
        'attr_values': attr_values,
        'box_arguments': box_arguments,
        'range_filter_dict': range_filter_dict,
        'INPUT_TYPE_RANGE': INPUT_TYPE_RANGE,
    }

    return render(request, 'product_by_category.html', context)


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
