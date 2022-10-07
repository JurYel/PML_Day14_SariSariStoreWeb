from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Inventory(models.Model):
    quantity = models.PositiveIntegerField(blank=False, null=False)
    item_name = models.CharField(max_length=50)
    price = models.FloatField(validators=[MinValueValidator(1.0)])
    item_img = models.ImageField(upload_to="img_items/", default="img_items/default_item_img.jpg")

    def __str__(self):
        return self.item_name

class CartItem(models.Model):
    item = models.OneToOneField(
        Inventory,
        on_delete=models.CASCADE,
        primary_key=False
    )
    item_bought = models.CharField(max_length=50)
    unit_price = models.FloatField(validators=[MinValueValidator(1.0)])
    qty_bought = models.PositiveIntegerField(blank=False, null=False)
    subtotal = models.FloatField(validators=[MinValueValidator(1.0)])

class Sales(models.Model):
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    quantity = models.PositiveIntegerField(blank=False, null=False)
    item_name = models.CharField(max_length=50)
    unit_price = models.FloatField(validators=[MinValueValidator(1.0)])
    subtotal = models.FloatField(validators=[MinValueValidator(1.0)])
