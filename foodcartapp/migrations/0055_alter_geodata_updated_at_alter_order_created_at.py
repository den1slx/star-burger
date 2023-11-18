# Generated by Django 4.2.4 on 2023-11-18 07:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_alter_geodata_options_alter_geodata_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geodata',
            name='updated_at',
            field=models.DateTimeField(null=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2023, 11, 18, 7, 15, 55, 822530, tzinfo=datetime.timezone.utc), verbose_name='Заказ сделан'),
        ),
    ]
