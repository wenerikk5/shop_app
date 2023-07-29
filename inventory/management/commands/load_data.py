import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from transliterate import slugify
import uuid

from inventory.models import (
    Category,
    Product,
    ProductItem,
    ProductAttribute,
    ProductAttributeValue,
    ProductItemAttribute
)


Models = {
    # Category: 'Category.csv',
    # Product: 'Product.csv',
    ProductItem: 'ProductItem.csv',
    ProductAttribute: 'ProductAttribute.csv',
    ProductAttributeValue: 'ProductAttributeValue.csv',
    ProductItem.attribute_value.through: 'ProductItemAttribute.csv',
}


class Command(BaseCommand):
    help = 'Загрузка данных из csv файлов'

    def handle(self, *args, **options):
        """Заполняем данные моделей информацией из CSV таблиц."""
        with open(f'{settings.BASE_DIR}/data/Category.csv', 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                c = Category.objects.create(
                    id=row['id'],
                    name=row['name'],
                    slug='slug',
                    parent_id=row['parent'],
                    lft=row['lft'],
                    rght=row['rght'],
                    level=row['level'],
                    is_active=row['is_active'],
                    tree_id=row['tree_id'],
                )
            print(f'Данные для таблицы Category успешно загружены')

        with open(f'{settings.BASE_DIR}/data/Product.csv', 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = slugify(row['name'])
                if len(name) > 12:
                    name = name[:12]
                tail = str(uuid.uuid4())[:6]
                slug = name + '-' + tail
                p = Product.objects.create(
                    id=row['id'],
                    name=row['name'],
                    slug=slug,
                    category_id=row['category_id'],
                    brand=row['brand'],
                    description=row['description'],
                )
            print(f'Данные для таблицы Product успешно загружены')

        for model, csv_files in Models.items():
            with open(
                f'{settings.BASE_DIR}/data/{csv_files}',
                'r',
                encoding='utf-8-sig'
            ) as csv_file:
                reader = csv.DictReader(csv_file, quoting=csv.QUOTE_MINIMAL)
                model.objects.bulk_create(
                    model(**data) for data in reader
                )
            self.stdout.write(
                f'Данные для таблицы {model.__name__} успешно загружены')
        return ('База данных успешно загружена.')
