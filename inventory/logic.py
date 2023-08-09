from inventory import models


def filter_products(checkbox_filter_dict, range_filter_dict, brand_dict,
                    price_dict, category):
    attr_names = list(checkbox_filter_dict.keys()) + list(range_filter_dict.keys())
    print('attr_names', attr_names)

    products_by_attributes = models.Product.objects\
        .filter(category=category)

    # filter checkbox args
    for name, values in checkbox_filter_dict.items():
        products_by_attributes = products_by_attributes\
            .filter(product__attribute_value__product_attribute__name__iexact=name,
                    product__attribute_value__value__in=values)

    product_ids = set(products_by_attributes.values_list('id', flat=True))

    # filter range args
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

        ids = set(attribute_values.values_list(
            'product_item__product__id',
            flat=True
        ))
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
            'product__media',
            'product__media__img_url',
        ).distinct('id')
    # filter by brand
    if brand_dict:
        products = products.filter(brand__in=brand_dict.get('brand'))
    # filter by price
    if price_dict.get('price', [0, 0])[0]:
        products = products.filter(product__price__gte=price_dict['price'][0])
    if price_dict.get('price', [0, 0])[1]:
        products = products.filter(product__price__lte=price_dict['price'][1])

    return products
