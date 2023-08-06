from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES,
                                      coerce=int)
    override = forms.BooleanField(required=False,
                                  initial=False,
                                  widget=forms.HiddenInput)


class CartAddHiddenProductForm(forms.Form):
    quantity = forms.TypedChoiceField(coerce=int,
                                      initial=1,
                                      widget=forms.HiddenInput)
    override = forms.BooleanField(required=False,
                                  initial=False,
                                  widget=forms.HiddenInput)


class CartForm(forms.Form):
    quantity = forms.TypedChoiceField(coerce=int,
                                      initial=1)
    override = forms.BooleanField(required=False,
                                  initial=False,
                                  widget=forms.HiddenInput)
    name = forms.CharField()
    id = forms.IntegerField()
