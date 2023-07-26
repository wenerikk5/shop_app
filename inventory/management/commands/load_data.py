import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from inventory.models import (
    Category,
    Product,
    ProductItem,
    ProductAttribute,
    ProductAttributeValue
)


Models = {
    # Category: 'Category.csv',
    Product: 'Product.csv',
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
                    slug=row['slug'],
                    parent_id=row['parent'],
                    lft=row['lft'],
                    rght=row['rght'],
                    level=row['level'],
                    is_active=row['is_active'],
                    tree_id=row['tree_id'],
                )
            print(f'Данные для таблицы Category успешно загружены')

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
