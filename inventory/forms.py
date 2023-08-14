from django import forms


class SearchForm(forms.Form):
    query = forms.CharField()


# delete
class ProductForm(forms.Form):
    slug_product = forms.CharField()
    name_product = forms.CharField()
    category_id = forms.IntegerField()
    description = forms.TextInput()

    sku = forms.CharField()

    name_attribute = forms.CharField()

    value_attribute = forms.CharField()


