from django import forms


class ProductForm(forms.Form):
    slug_product = forms.CharField()
    name_product = forms.CharField()
    category_id = forms.IntegerField()
    description = forms.TextInput()

    sku = forms.CharField()

    name_attribute = forms.CharField()

    value_attribute = forms.CharField()

# Product:
#     slug, name, category_id, description,

# product_item:
#     sku

# ProductAttribute:
#     category_id, name

# ProductAttributeValue:
#     product_attribute_id, value

# ProductItemAttribute:
#     product_item_id, product_attribute_value
