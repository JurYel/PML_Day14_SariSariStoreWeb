# Generated by Django 4.1.1 on 2022-10-05 03:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_remove_cartitem_item_bought_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='id',
            field=models.BigAutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='item',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventory'),
        ),
    ]
