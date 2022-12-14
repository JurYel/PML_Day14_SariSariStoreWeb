# Generated by Django 4.1.1 on 2022-10-04 10:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_alter_inventory_item_img'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty_bought', models.PositiveIntegerField()),
                ('item_bought', models.CharField(max_length=50)),
                ('item_price', models.FloatField(validators=[django.core.validators.MinValueValidator(1.0)])),
                ('item_image', models.ImageField(default='img_items/default_item_img.jpg', upload_to='img_items/')),
            ],
        ),
        migrations.AlterField(
            model_name='inventory',
            name='item_img',
            field=models.ImageField(default='img_items/default_item_img.jpg', upload_to='img_items/'),
        ),
    ]
