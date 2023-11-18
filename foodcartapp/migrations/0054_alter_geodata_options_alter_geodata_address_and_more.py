# Generated by Django 4.2.4 on 2023-11-18 07:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_alter_geodata_lat_alter_geodata_lng_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='geodata',
            options={'verbose_name': 'Геоданные', 'verbose_name_plural': 'Геоданные'},
        ),
        migrations.AlterField(
            model_name='geodata',
            name='address',
            field=models.TextField(unique=True, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='geodata',
            name='lat',
            field=models.FloatField(null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='geodata',
            name='lng',
            field=models.FloatField(null=True, verbose_name='Долгота'),
        ),
        migrations.AlterField(
            model_name='geodata',
            name='updated_at',
            field=models.DateTimeField(verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2023, 11, 18, 7, 14, 47, 175240, tzinfo=datetime.timezone.utc), verbose_name='Заказ сделан'),
        ),
    ]
