# Generated by Django 2.2 on 2020-03-03 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0012_auto_20200303_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(to='shop_app.CartProduct'),
        ),
    ]
