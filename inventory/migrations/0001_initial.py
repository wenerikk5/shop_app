# Generated by Django 4.2.3 on 2023-07-29 11:27

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('slug', models.CharField(max_length=180)),
                ('is_active', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='inventory.category')),
            ],
            options={
                'verbose_name': 'product category',
                'verbose_name_plural': 'product categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=200)),
                ('name', models.CharField(max_length=255)),
                ('brand', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('filtered', models.BooleanField(default=False)),
                ('filter_type', models.CharField(default='checkbox', max_length=20)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_attribute', to='inventory.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(db_index=True, max_length=200)),
                ('value_number', models.FloatField(blank=True, null=True)),
                ('product_attribute', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_attribute_values', to='inventory.productattribute')),
            ],
        ),
        migrations.CreateModel(
            name='ProductItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=20, unique=True)),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductItemAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_attribute_value', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productAttributeValue', to='inventory.productattributevalue')),
                ('product_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productItem', to='inventory.productitem')),
            ],
            options={
                'unique_together': {('product_attribute_value', 'product_item')},
            },
        ),
        migrations.AddField(
            model_name='productitem',
            name='attribute_value',
            field=models.ManyToManyField(related_name='product_item', through='inventory.ProductItemAttribute', to='inventory.productattributevalue'),
        ),
        migrations.AddField(
            model_name='productitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='item', to='inventory.product'),
        ),
    ]
