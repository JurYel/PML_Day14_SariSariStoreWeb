from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Inventory, Sales, CartItem
from .forms import ItemForm
from django.urls import reverse
from django.http import Http404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import string
import random

# Create your views here.
def index(request):
    """
        Fetches the grocery items, total count of cart items from the SQLite Database
        and displays it on the home page of the website.
    """
    template = loader.get_template("home.html")
    items = Inventory.objects.all().values()
    cart_items = CartItem.objects.all()
    context = {"items": items, "cart_items_count": len(cart_items)}
    return HttpResponse(template.render(context, request))

def inventory_page(request):
    """
        Fetches the grocery items in the Inventory model, the form fields,
        and displays it in the inventory page.
    """
    template = loader.get_template("inventory.html")
    items = Inventory.objects.all().values()
    form = ItemForm()
    context = {"items": items, "form": form, "url": "/inventory/add/", "is_update": False, "submit": "Add Item"}
    return HttpResponse(template.render(context, request))

def sales_record(request):
    """
        Retrieves all of the sales record and displays it on the
        sales_record html page.
    """
    template = loader.get_template("sales_record.html")
    sales = Sales.objects.all().values()
    context = {"sales": sales}
    return HttpResponse(template.render(context,request))

def items_cart(request):
    """
        Fetches all the ordered items from the grocery list, sorts it by
        price and displays it on the grocery_cart html page.
    """
    template = loader.get_template("grocery_cart.html")
    cart_items = CartItem.objects.all().order_by("unit_price").values()
    context = {"cart_items": cart_items,"is_checkout": False}
    return HttpResponse(template.render(context, request))

def add_to_cart(request, id):
    """
        Function that performs the process of adding the item to the cart,
        this stores the ordered item to the CartItem model and reduces
        the quantity of the item.
    """
    try:
        if request.method == 'POST':
            item = Inventory.objects.get(id=id)
            qty_bought = int(request.POST['qty-bought'])
            subtotal = qty_bought * item.price

            if CartItem.objects.filter(item=item).exists():
                cart_item = CartItem.objects.filter(item=item).first()
                qty_bought = int(cart_item.qty_bought + qty_bought)
                cart_item.qty_bought = qty_bought
                cart_item.subtotal = float(qty_bought * item.item_price)
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(item=item, qty_bought=qty_bought,
                                                    item_bought=item.item_name, subtotal=subtotal,
                                                    unit_price=item.price)
                cart_item.save()

            item.quantity = int(item.quantity - qty_bought)
            item.save()

            return HttpResponseRedirect(reverse('home'))
    except Inventory.DoesNotExist:
        raise Http404("Add-Cart Error: Item with such id does not exist")

    items = Inventory.objects.all().values()
    context = {"items": items,"is_checkout": False, "cart_items_count": 0}
    template = loader.get_template("home.html")
    return HttpResponse(template.render(context, request))

def delete_cart_item(request, id):
    """
        Performs deletion of item in the cart, and updates
        the quantity of the item in Inventory after deletion.
    """
    try:
        cart_item = CartItem.objects.get(id=id)
        item = Inventory.objects.filter(item_name=cart_item.item.item_name).first()
        item.quantity = int(item.quantity + cart_item.qty_bought)
        item.save()
        cart_item.delete()
    except CartItem.DoesNotExist:
        raise Http404("Delete CartItem Error: Failed to delete cart item")

    return HttpResponseRedirect(reverse('items_cart'))

def increase_qty_bought(request, id):
    """
        Increases the quantity of the item bought by updating
        the item in the CartItem model and reducing the quantity of
        the item in the Inventory then recompute the subtotal of the
        purchased item.
    """
    try:
        cart_item = CartItem.objects.get(id=id)
        item = Inventory.objects.filter(item_name=cart_item.item.item_name).first()
        qty_bought = cart_item.qty_bought + 1
        cart_item.qty_bought = qty_bought
        cart_item.subtotal = float(qty_bought * cart_item.unit_price)
        item.quantity = item.quantity - 1
        cart_item.save()
        item.save()
        return HttpResponseRedirect(reverse("items_cart"))
    except CartItem.DoesNotExist:
        raise Http404("Increase Quantity Error: Failed to increase item quantity bought")

def decrease_qty_bought(request, id):
    """
        Decreases the quantity of the item bought by updating
        the item in the CartItem model and reducing the quantity of
        the item in the Inventory then recompute the subtotal of the
        purchased item.
    """
    try:
        cart_item = CartItem.objects.get(id=id)
        item = Inventory.objects.filter(item_name=cart_item.item.item_name).first()
        qty_bought = cart_item.qty_bought - 1
        cart_item.qty_bought = qty_bought
        cart_item.subtotal = float(qty_bought * cart_item.unit_price)
        item.quantity = item.quantity + 1
        cart_item.save()
        item.save()
        return HttpResponseRedirect(reverse("items_cart"))
    except CartItem.DoesNotExist:
        raise Http404("Decrease Quantity Error: Failed to decrease item quantity bought")

def proceed_to_pay(request):
    """
        Performs the process of proceed_to_pay:
        1. Calculate the total price
        2. Get the total items bought
        3. Get the current date & time for receipt generation
        4. Generates the invoice number of the purchase
        5. Render everything to grocery_cart page along with the
            generation of the receipt.
    """
    date_time = datetime.now().strftime("%b %d, %Y, %I:%M %p")
    invoice_num = generate_invoice_num()

    cart_items = CartItem.objects.all().order_by("unit_price").values()

    if len(cart_items) > 0:
        total_price = 0
        for cart_item in cart_items:
            total_price += float(cart_item['subtotal'])
    else:
        return HttpResponseRedirect(reverse('items_cart'))

    context = {"total_price": total_price, "item_counts": len(cart_items), "is_checkout": True,
               "cart_items": cart_items, "ordered_items": cart_items, "date_time": date_time,
               "invoice_num": invoice_num}
    template = loader.get_template("grocery_cart.html")
    return HttpResponse(template.render(context, request))

def generate_invoice_num(size=6, chars=string.ascii_uppercase + string.digits):
    """
        Generates a random invoice number with a length of 6 containing
        random uppercase letters and digits.

        Source: https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    """
    return ''.join(random.choice(chars) for _ in range(size))

def record_sales(request):
    """
        Records the purchase of the item to the Sales model then
        deletes the items in the CartItem model.
    """
    date_time = datetime.now().strftime("%b %d, %Y, %I:%M %p")
    cart_items = CartItem.objects.all().values()
    for cart_item in cart_items:
        sale_record = Sales.objects.create(quantity=cart_item['qty_bought'], item_name=cart_item['item_bought'],
                            unit_price=cart_item['unit_price'], subtotal=cart_item['subtotal'])
        sale_record.save()

    CartItem.objects.all().delete()

    return HttpResponseRedirect(reverse('home'))


def add_item(request):
    """
        Performs creation of item in Inventory model:
        1. Fetches the inputs from the add form
        2. Checks the validity of the form inputs
        3. Cleans and gets data from the form
        4. Creates a new item in the inventory
        5. Sends a success message after creation otherwise throws an exception.
    """
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item_img = form.cleaned_data.get("item_img")
            item_name = form.cleaned_data.get("item_name")
            qty = form.cleaned_data.get("quantity")
            price = form.cleaned_data.get("price")

            item = Inventory.objects.create(item_img=item_img,
                                            item_name=item_name,
                                            quantity=qty,
                                            price=price)
            item.save()

            messages.success(request, "Item added successfully")
            return HttpResponseRedirect(reverse('inventory_page'))
    else:
        form = ItemForm()
    context = {"form": form}
    template = loader.get_template("inventory.html")
    # return HttpResponseRedirect(reverse('inventory_page'))
    return HttpResponse(template.render(context, request))

def delete_fetch_item(request, id):
    """
        Fetches the item to be deleted then fills the form
        with the fetched item.
    """
    try:
        item = Inventory.objects.get(id=id)
        items = Inventory.objects.all().values()
        form = ItemForm(instance=item)
        template = loader.get_template("inventory.html")
        context = {"form": form, "items": items, "submit": "Delete Item", "is_update": False, "url": "/inventory/delete/delete_item/" + str(id)}
    except Inventory.DoesNotExist:
        raise Http404("Fetch Error: Item with such id does not exist")

    return HttpResponse(template.render(context, request))

def delete_record(request, id):
    """
        Deletes the item from the Inventory model then
        sends a success message after, otherwise throws
        an exception.
    """
    try:
        item = Inventory.objects.get(id=id)
        messages.success(request, f"{item} deleted successfully")
        item.delete()
    except Inventory.DoesNotExist:
        raise Http404("Delete Error: Failed to delete item")

    return HttpResponseRedirect(reverse("inventory_page"))

def update_fetch_item(request, id):
    """
        Fetches the item to be deleted then fills the
        form with the fetched item
    """
    try:
        item = Inventory.objects.get(id=id)
        items = Inventory.objects.all().values()
        form = ItemForm(instance=item)
        template = loader.get_template("inventory.html")
        context = {"form": form, "item": item, "items": items, "submit": "Update Item", "is_update": True}
    except Inventory.DoesNotExist:
        raise Http404("Fetch Error: Item with such id does not exist")

    return HttpResponse(template.render(context, request))

def update_record(request, id):
    """
        Updates the fetched item with the filled up form then
        sends a success message after update otherwise throws an
        exception.
    """
    try:
        if request.method == 'POST':
            form = ItemForm(request.POST, request.FILES)
            if form.is_valid():
                item = Inventory.objects.get(id=id)
                item.item_img = form.cleaned_data.get("item_img")
                item.item_name = form.cleaned_data.get("item_name")
                item.quantity = form.cleaned_data.get("quantity")
                item.price = form.cleaned_data.get("price")

            item.save()
            messages.success(request, f"{item} updated successfully")
            return HttpResponseRedirect(reverse("inventory_page"))
    except Inventory.DoesNotExist:
        raise Http404("Update Error: Failed to update item")

    return HttpResponseRedirect(reverse("inventory_page"))

def search_sales_by_key(request):
    """
        Filters Sales model with Item name
    """
    try:
        if request.method == 'GET':
            search_key = request.GET['search-input']
            if Sales.objects.filter(item_name=search_key.title()).exists():
                sales = Sales.objects.filter(item_name=search_key.lower().title())
                context = {"sales": sales}
                template = loader.get_template("sales_record.html")
                return HttpResponse(template.render(context, request))
            else:
                return HttpResponseRedirect(reverse("sales_record"))
    except ObjectDoesNotExist:
        raise Http404("Search Error: Record with such filter does not exist")

def search_sales_by_datetime(request):
    """
        Incomplete function: Performs query to filter by datetime range
    """
    try:
        return HttpResponseRedirect(reverse("sales_record"))
    except ObjectDoesNotExist:
        raise Http404("Search Error: Record with such filter does not exist")
