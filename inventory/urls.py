from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('inventory/', include([
        path('', views.inventory_page, name='inventory_page'),
        path('add/', views.add_item, name='add_item'),
        path('delete/', include([
            path('<int:id>/', views.delete_fetch_item, name='delete_fetch'),
            path('delete_item/<int:id>', views.delete_record, name='delete')
        ])),
        path('update/', include([
            path('<int:id>/', views.update_fetch_item, name='update_fetch'),
            path('update_item/<int:id>', views.update_record, name="update")
        ]))
    ])),
    path('sales/', include([
        path('', views.sales_record, name='sales_record'),
        path('search_by_key/', views.search_sales_by_key, name="search_by_key"),
        path('search_by_datetime/', views.search_sales_by_datetime, name="search_by_datetime")
    ])),
    path('mycart/', include([
        path('', views.items_cart, name='items_cart'),
        path('delete_cart_item/<int:id>', views.delete_cart_item, name='delete_cart_item'),
        path('proceed_to_pay/', views.proceed_to_pay, name='proceed_to_pay'),
        path('increase_qty/<int:id>', views.increase_qty_bought, name='increase_qty_bought'),
        path('decrease_qty/<int:id>', views.decrease_qty_bought, name='decrease_qty_bought'),
        path('record_sales/', views.record_sales, name='record_sales')
    ])),
    path('add_to_cart/<int:id>', views.add_to_cart, name='add_to_cart'),

]