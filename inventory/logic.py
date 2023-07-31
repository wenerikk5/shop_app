from inventory import models


def filter_products(checkbox_filter_dict, range_filter_dict, brand_dict,
                    price_dict, category):
    attr_names = list(checkbox_filter_dict.keys()) + list(range_filter_dict.keys())
    print('attr_names', attr_names)

    products_by_attributes = models.Product.objects\
        .filter(category=category)

    for name, values in checkbox_filter_dict.items():
        products_by_attributes = products_by_attributes\
            .filter(product__attribute_value__product_attribute__name__iexact=name,
                    product__attribute_value__value__in=values)\
            .values(
                'id',
                'product__attribute_value__product_attribute__name',
                'product__attribute_value__value'
            )

    if checkbox_filter_dict:
        product_ids = set([x.get('id') for x in products_by_attributes])
    else:
        product_ids = set([x.id for x in products_by_attributes])

    for name, values in range_filter_dict.items():
        attribute_values = models.ProductAttributeValue.objects\
            .filter(product_item__product__id__in=product_ids)\
            .filter(product_attribute__name__iexact=name)
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

    products = models.Product.objects\
        .filter(id__in=product_ids)\
        .values(
            'id',
            'name',
            'slug',
            'brand',
            'category__name',
            'product__price',
            'description',
        )
    if brand_dict:
        products = products.filter(brand__in=brand_dict.get('brand'))
    if price_dict.get('price', [0, 0])[0]:
        products = products.filter(product__price__gte=price_dict['price'][0])
    if price_dict.get('price', [0, 0])[1]:
        products = products.filter(product__price__lte=price_dict['price'][1])

    return products
