from django.forms import ModelForm
from inventory.models import Inventory
from django import forms

class ItemForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ('item_img', 'item_name', 'quantity', 'price')

        labels={
            "item_img": "Item Image",
            "item_name": "Item Name",
            "quantity": "Quantity",
            "price": "Price"
        }
        widgets = {
            'item_img': forms.FileInput(attrs={'class': 'form-control'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control qty-input'}),
            'price': forms.TextInput(attrs={'class': 'form-control price-input'})
        }