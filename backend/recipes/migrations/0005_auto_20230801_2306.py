# Generated by Django 3.2.16 on 2023-08-01 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230731_1431'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('-id',), 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-id',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество'),
        ),
    ]
