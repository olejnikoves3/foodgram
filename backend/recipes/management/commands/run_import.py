import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def ingredients(self, csv_reader):
        if not Ingredient.objects.exists():
            ingredients_for_create = [
                Ingredient(name=row[0], measurement_unit=row[1])
                for row in csv_reader
            ]
            Ingredient.objects.bulk_create(ingredients_for_create)

    def handle(self, *args, **kwargs):
        csv_file_path = '../data/ingredients.csv'
        with open(csv_file_path, 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            self.ingredients(reader)
