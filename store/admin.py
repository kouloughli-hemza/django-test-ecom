from django.contrib import admin
from django.db.models import QuerySet
from django.db.models.aggregates import Count
from .models import Collection, Product, Order, Customer
from django.utils.html import format_html, urlencode
from django.urls import reverse

PER_PAGE = 10


class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory status'
    parameter_name = 'inventory_status'

    def lookups(self, request, model_admin):
        return [
            ('>10', 'Low Stock')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '>10':
            return queryset.filter(inventory__lt='10')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price', 'inventory_status']
    list_per_page = PER_PAGE
    list_filter = ['collection', 'last_update', InventoryFilter]

    @admin.display(ordering="inventory")
    def inventory_status(self, product: Product):
        if product.inventory < 10:
            return 'Low stock'
        return 'Good stock'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset: QuerySet):
        updated_count = queryset.update(inventory=0)
        return self.message_user(request,
                                 f'inventory cleared for  {updated_count} products')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    list_display = ['payment_status', 'placed_at', 'customer_full_name']
    list_per_page = PER_PAGE
    list_select_related = ['customer']

    def customer_full_name(self, order: Order):
        return order.customer.first_name + ' ' + order.customer.last_name


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_per_page = PER_PAGE
    list_display = ['first_name', 'last_name', 'email', 'membership',
                    'order_count']
    list_editable = ['membership']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(order_count=Count("order")).order_by(
            '-order_count')
        return queryset

    def order_count(self, customer):
        return customer.order_count


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'total_products']
    list_per_page = PER_PAGE

    def total_products(self, collection: Collection):
        url = (reverse('admin:store_product_changelist') + '?' +
               urlencode({'collection_id': str(collection.id)})
               )
        return format_html('<a href="{}">{}</a>', url,
                           collection.total_products)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_products=Count('product')
        )
