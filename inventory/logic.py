from inventory import models


def filter_product(box_filter_dict, range_filter_dict, category):
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
    return product_ids
