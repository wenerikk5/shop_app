from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib.postgres.aggregates import ArrayAgg
from mptt.forms import TreeNodeChoiceField

from django.db.models.functions import Cast
from django.db.models import IntegerField

from inventory import models, forms


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
                print(item.split('-min'))
                if limit == 'min':
                    range_filter_dict.setdefault(name, [None, None])[0] = int(value)
                else:
                    range_filter_dict.setdefault(name, [None, None])[1] = int(value)

            print('range_filter_dict', range_filter_dict)


        products = models.Product.objects.filter(category=category)

        for name in box_filter_dict.keys():
            products = products\
                .filter(category__product_attribute__name=name,
                        product__attribute_value__value__in=box_filter_dict[name]
                        ).distinct()

        attribute_value_ids = []

        attribute_values = models.ProductAttributeValue.objects\
            .filter(product_attribute__category=category)
        for name in range_filter_dict.keys():
            if range_filter_dict[name][0] and range_filter_dict[name][1]:
                attribute_values = attribute_values\
                    .filter(product_attribute__name=name)\
                    .annotate(val_integer=Cast('value', output_field=IntegerField()))\
                    .filter(
                        val_integer__gte=range_filter_dict[name][0],
                        val_integer__lte=range_filter_dict[name][1]
                    ).distinct().values('id')
            elif range_filter_dict[name][0]:
                attribute_values = attribute_values\
                    .filter(product_attribute__name=name)\
                    .annotate(val_integer=Cast('value', output_field=IntegerField()))\
                    .filter(val_integer__gte=range_filter_dict[name][0])\
                    .distinct().values('id')
            else:
                attribute_values = attribute_values\
                    .filter(product_attribute__name=name)\
                    .annotate(val_integer=Cast('value', output_field=IntegerField()))\
                    .filter(val_integer__lte=range_filter_dict[name][1])\
                    .values('id')

            attribute_value_ids.extend(attribute_values)
            print('attriubte_values:', attribute_values)

        print('attribute_value_ids:', attribute_value_ids)

        attribute_value_ids = [x.get('id') for x in attribute_value_ids]

        if attribute_value_ids:
            products = products\
                .filter(product__attribute_value__id__in=attribute_value_ids)\
                .distinct()






            # results.extend(
            #     products
            #     .filter(category__product_attribute__name=key,
            #             product__attribute_value__value__in=filter_dict[key]
            #             )
            # )
        # print('results:', results)
        # count_results = {}

        # for product in results:
        #     count_results[product.id] = count_results.setdefault(product.id, 0) + 1
        
        # print('count results:', count_results)
        
        # l = len(filter_dict.keys())
        # res_ids = [key for key, value in count_results.items() if value >= l]

        # print('res_ids:', res_ids)

        # products = products.filter(id__in=res_ids)



        # products = models.Product.objects\
        #     .filter(category=category)\
        #     .filter(product__attribute_value__argument_value__in=filter_arguments)\
        #     .annotate(num_tags=Count('product__attribute_value'))\
        #     .filter(num_tags__gte=len(filter_arguments))\
        #     .values(
        #         'id',
        #         'name',
        #         'slug',
        #         'category__name',
        #         'description',
        #         'num_tags'
        #     )
        # print(products)
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

    return render(request,
                  'product_by_category.html',
                  context
                  )


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
        attribute_value = models.ProductAttributeValue.objects.create(
            product_attribute=product_attribute,
            value=cd.get('value_attribute')
        )

        product_item = models.ProductItem.objects.create(
            sku=cd.get('sku'),
            product=product
        )
        print('=====ITEM ADDED')
        return redirect('inventory:categories')
    return render(request, 'add_product.html', {'form': form})
