# Generated by Django 2.2 on 2020-03-14 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0025_order_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cvv',
            field=models.CharField(max_length=255),
        ),
    ]
