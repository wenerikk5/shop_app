from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib.postgres.aggregates import ArrayAgg
from mptt.forms import TreeNodeChoiceField

from django.db.models.functions import Cast

from django.contrib.postgres.search import SearchVector

from inventory import models, forms
from .recommender import Recommender
from .logic import filter_products
from cart.forms import CartAddProductForm, CartAddHiddenProductForm, CartForm
from .forms import SearchForm


def home(request):
    return render(request, 'index.html')


def category(request, category_slug=None):
    if category_slug:
        current_category = get_object_or_404(models.Category,
                                             slug=category_slug)

    all_categories = models.Category.objects.select_related('parent')
    categories_dict = {}

    for cat in all_categories:
        if cat.parent:
            key = cat.parent.id
        else:
            key = 0
        categories_dict.setdefault(key, []).append(cat)

    if category_slug:
        context = {
            'current_category': current_category,
            'categories': categories_dict.get(current_category.id),
            'categories_dict': categories_dict
        }
    else:
        context = {
            'categories': all_categories,
            'categories_dict': categories_dict
        }
    return render(request, 'category.html', context)


def product_by_category(request, category_slug):
    category = get_object_or_404(models.Category, slug=category_slug)

    checkbox_arguments = []
    range_arguments = []
    brand_arguments = []
    price_arguments = []

    checkbox_filter_dict = {}
    range_filter_dict = {}
    brand_dict = {}
    price_dict = {}

    if request.method == 'POST' and (
        len(request.POST.get('checkbox_attrs')) > 0
        or
        len(request.POST.get('range_attrs')) > 0
        or
        len(request.POST.get('brand_attrs')) > 0
        or
        len(request.POST.get('price_attrs')) > 0
    ):
        if len(request.POST.get('checkbox_attrs')) > 0:
            checkbox_arguments = request.POST.get('checkbox_attrs').split('&')
            for item in checkbox_arguments:
                name, value = item.split(':')
                checkbox_filter_dict.setdefault(name, []).append(value)
            print('box_filter_dict:', checkbox_filter_dict)

        if len(request.POST.get('range_attrs')) > 0:
            range_arguments = request.POST.get('range_attrs').split('&')
            for item in range_arguments:
                name, value = item.split(':')
                name, limit = name.split('-')
                if limit == 'min':
                    range_filter_dict.setdefault(name, [None, None])[0] = float(value)
                else:
                    range_filter_dict.setdefault(name, [None, None])[1] = float(value)
            print('range_filter_dict', range_filter_dict)

        if len(request.POST.get('brand_attrs')) > 0:
            brand_arguments = request.POST.get('brand_attrs').split('&')
            for item in brand_arguments:
                name, value = item.split(':')
                brand_dict.setdefault(name, []).append(value)
            print('brand_dict:', brand_dict)

        if len(request.POST.get('price_attrs')) > 0:
            price_arguments = request.POST.get('price_attrs').split('&')
            for item in price_arguments:
                name, value = item.split(':')
                name, limit = name.split('-')
                if limit == 'min':
                    price_dict.setdefault(name, [None, None])[0] = float(value)
                else:
                    price_dict.setdefault(name, [None, None])[1] = float(value)
            print('price_dict', price_dict)

        products = filter_products(checkbox_filter_dict, range_filter_dict,
                                   brand_dict, price_dict, category)
    else:
        products = models.Product.objects\
            .filter(category=category)\
            .values(
                'id',
                'name',
                'slug',
                'brand',
                'category__name',
                'product__price',
                'product__sku',
                'product__media__img_url',
            )\
            .order_by('product__price')
    unique_prods = []

    for i in range(len(products)):
        if i == 0 or products[i].get('id') != products[i-1].get('id'):
            unique_prods.append(products[i])

    # all attributes for certain category (list in filters)
    category_attrs = models.ProductAttribute.objects.filter(
        category=category, filtered=True)

    # attribute values (checkbox values in filters)
    attr_values = models.ProductAttributeValue.objects\
        .filter(product_attribute__category__id=category.id)\
        .filter(product_attribute__filtered=True)\
        .values(
            'value',
            'product_attribute__name',
            'product_attribute__category__id',
        )\
        .distinct()

    # all values for products in certain category (checkbox values in filter)
    brands = models.Product.objects\
        .filter(category__id=category.id)\
        .values('brand')\
        .distinct()

    context = {
        'products': unique_prods,
        'category': category,
        'category_attrs': category_attrs,
        'attr_values': attr_values,
        'checkbox_arguments': checkbox_arguments,
        'range_filter_dict': range_filter_dict,
        'brands': brands,
        'brand_dict': brand_dict,
        'price_dict': price_dict,
        'cart_product_form': CartAddHiddenProductForm()
    }
    return render(request, 'product_by_category.html', context)


def product_detail(request, product_slug):
    filter_arguments = []

    category = get_object_or_404(models.Category, product__slug=product_slug)

    sku_values = models.Product.objects\
        .filter(slug=product_slug)\
        .values_list('product__sku', flat=True)

    if request.GET:
        for value in request.GET.values():
            filter_arguments.append(value)

        product = models.ProductItem.objects\
            .filter(product__slug=product_slug)\
            .filter(sku__in=filter_arguments)\
            .values(
                'id',
                'sku',
                'price',
                'product__id',
                'product__name',
                'product__description',
                'media',
                'media__img_url',
            )\
            .order_by('price')[0]

        # NEEDS CHECK
        if len(product) < 1:
            product = models.ProductItem.objects\
                .filter(product__slug=product_slug)\
                .filter(sku__in=filter_arguments)\
                .values(
                    'id',
                    'sku',
                    'price',
                    'product__id',
                    'product__name',
                    'product__description',
                    'media',
                    'media__img_url',
                )[0]

    else:
        product = models.ProductItem.objects\
            .filter(product__slug=product_slug)\
            .values(
                'id',
                'sku',
                'price',
                'product__id',
                'product__name',
                'product__description',
                'media',
                'media__img_url',
            )\
            .order_by('price')[0]
        filter_arguments.append(product.get('sku'))

    attrs = models.ProductItem.objects\
        .filter(sku__in=filter_arguments)\
        .values(
            'attribute_value__value',
            'attribute_value__product_attribute__name'
            )

    cart_product_form = CartAddProductForm()

    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)
    # print('====product_item:', product)
    # print('====recommended products:', recommended_products

    context = {
        'product': product,
        'category': category,
        'attrs': attrs,
        'sku_values': sku_values,
        'cart_product_form': cart_product_form,
        'filter_args': filter_arguments,
        'recommended_products': recommended_products,
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


def product_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = models.Product.objects.annotate(
                search=SearchVector('name', 'description', 'brand'),
            ).filter(search=query)

    context = {'form': form,
               'query': query,
               'products': results}
    return render(request, 'search.html', context)
