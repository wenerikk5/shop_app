from typing import Iterable, Optional
from django.db import models
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey,\
    TreeManyToManyField

from transliterate import slugify
import uuid


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
    img_url = models.ImageField(upload_to='category/%Y/%m/%d',
                                blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'product category'
        verbose_name_plural = 'product categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        name = slugify(self.name)
        if len(name) > 50:
            name = name[:50]
        tail = str(uuid.uuid4())[:6]

        self.slug = name + '-' + tail
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("inventory:category",
                       kwargs={"category_slug": self.slug})


class Product(models.Model):
    slug = models.SlugField(
        max_length=200,
    )
    name = models.CharField(max_length=255,)
    category = TreeForeignKey(
        Category,
        on_delete=models.PROTECT,
    )
    brand = models.CharField(
        max_length=100,
        null=False,
        blank=False,
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        name = slugify(self.name)
        if len(name) > 30:
            name = name[:30]
        tail = str(uuid.uuid4())[:6]

        self.slug = name + '-' + tail
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("inventory:product_detail",
                       kwargs={"product_slug": self.slug})


class ProductItem(models.Model):
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
        related_name='product_item',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
    )
    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sku']
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f'Product item sku={self.sku}'

    def get_slug(self):
        return Product.objects.filter(product__sku=self.sku)[0].slug

    def get_name(self):
        return Product.objects.filter(product__sku=self.sku)[0].name

    def get_absolute_url(self):
        return reverse("inventory:product_detail",
                       kwargs={"product_slug": self.get_slug()})


class ProductAttribute(models.Model):
    name = models.CharField(
        max_length=255,
        db_index=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='product_attribute'
    )
    filtered = models.BooleanField(
        default=False,
        null=False,
        blank=False
    )
    filter_type = models.CharField(
        max_length=20,
        default='checkbox'
    )

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    product_attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.PROTECT,
        related_name='product_attribute_values'
    )
    value = models.CharField(
        max_length=200,
        db_index=True,
    )
    value_number = models.FloatField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'id: {self.id}, value: {self.value}'

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class ProductItemAttribute(models.Model):
    product_item = models.ForeignKey(
        ProductItem,
        related_name='productItem',
        on_delete=models.PROTECT,
    )
    product_attribute_value = models.ForeignKey(
        ProductAttributeValue,
        related_name='productAttributeValue',
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = (("product_attribute_value", "product_item"),)


class ProductMedia(models.Model):
    img_url = models.ImageField(upload_to='product/%Y/%m/%d',
                                blank=True, null=True)
    product_item = models.ForeignKey(
        ProductItem,
        on_delete=models.CASCADE,
        related_name='media'
    )
    alt_text = models.CharField(max_length=50, default='Product images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Product image id={self.id}'
