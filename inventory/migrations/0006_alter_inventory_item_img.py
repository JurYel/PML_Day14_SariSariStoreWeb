# Generated by Django 4.1.1 on 2022-10-03 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_alter_inventory_item_img_alter_inventory_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='item_img',
            field=models.ImageField(default='inventory/uploads/img_items/default_item_img.jpg', upload_to='media/img_items'),
        ),
    ]