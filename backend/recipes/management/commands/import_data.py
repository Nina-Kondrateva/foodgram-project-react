from csv import DictReader
from django.core.management import BaseCommand

from recipes.models import Ingredient

MODEL_FILE = [
    (Ingredient, './data/ingredients.csv'),
]


class Command(BaseCommand):
    """Загрузка базы данных из csv файла."""

    def handle(self, *args, **options):
        for model, fils in MODEL_FILE:
            fieldnames = ['name', 'measurement_unit']
            with open(fils, newline='') as csvfile:
                record = []
                for row in DictReader(csvfile, fieldnames=fieldnames):
                    records = model(**row)
                    record.append(records)
                if model.objects.exists():
                    model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(
                        f'Данные модели {model} удалены!'))
                model.objects.bulk_create(record)
                self.stdout.write(self.style.SUCCESS(
                    f'Данные модели {model} загружены!))'))
