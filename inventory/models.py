from typing import Iterable, Optional
from django.db import models

from mptt.models import MPTTModel, TreeForeignKey,\
    TreeManyToManyField


class Category(MPTTModel):
    name = models.CharField(
        max_length=150,
        unique=False,
    )
    slug = models.CharField(
        max_length=180,
        unique=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='children',
        null=True,
        blank=True,
        unique=False,
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'product category'
        verbose_name_plural = 'product categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    slug = models.SlugField(
        max_length=200,
    )
    name = models.CharField(max_length=255,)
    category = TreeForeignKey(
        Category,
        on_delete=models.PROTECT,
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ProductItem(models.Model):
    # slug = models.SlugField(
    #     max_length=200,
    # )
    sku = models.CharField(
        max_length=20,
        unique=True,
    )
    product = models.ForeignKey(
        Product,
        related_name="product",
        on_delete=models.PROTECT
    )
    attribute_value = models.ManyToManyField(
        'ProductAttributeValue',
        through='ProductItemAttribute',
    )
    # created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Product item sku={self.sku}'


class ProductAttribute(models.Model):
    name = models.CharField(
        max_length=255,
        # unique=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='product_attribute'
    )

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    product_attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.PROTECT,
        related_name='product_attribute'
    )
    value = models.CharField(
        max_length=200,
    )
    argument_value = models.CharField(
        max_length=255,
    )

    # def __str__(self):
    #     return self.id

    def save(self, *args, **kwargs):
        self.argument_value = f'{self.product_attribute.name}:{self.value}'
        return super().save(*args, **kwargs)


class ProductItemAttribute(models.Model):
    product_item = models.ForeignKey(
        ProductItem,
        related_name='product_item',
        on_delete=models.PROTECT,
    )
    product_attribute_value = models.ForeignKey(
        ProductAttributeValue,
        related_name='product_attribute_value',
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = (("product_attribute_value", "product_item"),)
