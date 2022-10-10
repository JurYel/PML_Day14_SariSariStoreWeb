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
import dateutil.parser as dtparser

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
    context = {"items": items, "form": form, "url": "/inventory/add/", "is_update": False, "is_delete": False,"submit": "Add Item"}
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

def add_to_cart(request, id, qty=None):
    """
        Function that performs the process of adding the item to the cart,
        this stores the ordered item to the CartItem model and reduces
        the quantity of the item.
    """
    print("add_to_cart method reached")
    try:
        if request.method == 'POST':
            item = Inventory.objects.get(id=id)
            if qty:
                qty_bought = qty
            else:
                qty_bought = int(request.POST['qty-bought'])

            if qty_bought > item.quantity:
                messages.error(request, "Quantity exceeds remaining item quantity.")
                return HttpResponseRedirect(reverse('home'))
            elif qty_bought < 1:
                messages.error(request, "Quantity must be greater than 1.")
                return HttpResponseRedirect(reverse('home'))

            subtotal = qty_bought * item.price

            if CartItem.objects.filter(item_bought=item.item_name).exists():
                cart_item = CartItem.objects.filter(item_bought=item.item_name).first()
                cart_item_qty = int(cart_item.qty_bought + qty_bought)
                cart_item.qty_bought = cart_item_qty
                cart_item.subtotal = float(cart_item_qty * item.price)
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(item_img=item.item_img,
                                                    qty_bought=qty_bought,item_bought=item.item_name,
                                                    subtotal=subtotal,unit_price=item.price)
                cart_item.save()

            item.quantity = int(item.quantity - qty_bought)
            print(qty_bought)
            item.save()

            if item.quantity <= 0:
                item.quantity = 0
                item.save()

        return HttpResponseRedirect(reverse('home'))
    except Inventory.DoesNotExist:
        raise Http404("Add-Cart Error: Item with such id does not exist")

    items = Inventory.objects.all().values()
    context = {"items": items,"is_checkout": False, "cart_items_count": 0}
    template = loader.get_template("home.html")
    return HttpResponse(template.render(context, request))

def check_age(request, id, qty):
    if request.method == 'POST':
        age = int(request.POST['age'])
        if age < 18:
            messages.error(request,f"Naku, bawal ka pa po nyan, balik ka nalang po in {18-age} years.")
            return HttpResponseRedirect(reverse('home'))
        else:
            add_to_cart(request, id, qty)

    return HttpResponseRedirect(reverse('home'))

def delete_cart_item(request, id):
    """
        Performs deletion of item in the cart, and updates
        the quantity of the item in Inventory after deletion.
    """
    try:
        cart_item = CartItem.objects.get(id=id)
        item = Inventory.objects.filter(item_name=cart_item.item_bought).first()
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
        item = Inventory.objects.filter(item_name=cart_item.item_bought).first()
        if item.quantity == 0:
            messages.error(request, "Cant increase quantity, item is out of stock")
            return HttpResponseRedirect(reverse('items_cart'))
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
        item = Inventory.objects.filter(item_name=cart_item.item_bought).first()
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
    if Inventory.objects.filter(quantity=0).exists():
        item = Inventory.objects.filter(quantity=0).first()

    for cart_item in cart_items:
        if item.item_name == cart_item['item_bought']:
            item.delete()
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
            item_img = request.FILES["item_img"]
            item_name = form.cleaned_data.get("item_name")
            qty = form.cleaned_data.get("quantity")
            price = form.cleaned_data.get("price")

            if qty == 0:
                messages.error(request, "Quantity can't be less than 1.")
                return HttpResponseRedirect(reverse('inventory_page'))
            if price == 0.0:
                messages.error(request, "Please input a price for the item.")
                return HttpResponseRedirect(reverse('inventory_page'))

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
        context = {"form": form, "items": items, "item": item,"submit": "Delete Item", "is_update": False,
                   "is_delete": True,"url": "/inventory/delete/delete_item/" + str(id)}
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
        context = {"form": form, "item": item, "items": items, "submit": "Update Item",
                   "is_update": True, "is_delete": False}
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
                print(form.cleaned_data.get('item_img'))
                if str(form.cleaned_data.get("item_img")).find("default_item_img") == -1:
                    item.item_img = request.FILES["item_img"]
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
        if request.method == 'GET':
            if request.GET['datetimes'] == '':
                return HttpResponseRedirect(reverse('sales_record'))
            dtime1 = dtparser.parse(request.GET['datetimes'].split('-')[0], fuzzy=True)
            dtime2 = dtparser.parse(request.GET['datetimes'].split('-')[1], fuzzy=True)
            # print("dtime1", dtparser.parse(dtime1, fuzzy=True))
            # print("dtime2", dtparser.parse(dtime2, fuzzy=True))
            print(type(dtime1))

            sales = Sales.objects.filter(datetime__gte=dtime1, datetime__lte=dtime2)
            context = {"sales": sales}
            template = loader.get_template("sales_record.html")

            return HttpResponse(template.render(context, request))
    except ObjectDoesNotExist:
        raise Http404("Search Error: Record with such filter does not exist")
