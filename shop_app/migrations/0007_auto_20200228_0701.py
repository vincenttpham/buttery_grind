# Generated by Django 2.2 on 2020-02-28 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0006_auto_20200228_0700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
    ]
