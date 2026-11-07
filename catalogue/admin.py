from django.contrib import admin

from .models import (
    Category,
    Product,
    Supplier,
    SupplierProduct,
    PriceHistory,
    calculate_price_intelligence,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'unit',
        'is_active',
    )
    list_filter = ('category', 'is_active')
    search_fields = ('name',)

    

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'category',
        'location',
        'is_verified',
        'is_active',
        'performance_orders',
        'performance_fulfilment',
        'performance_on_time',
        'performance_lead_time',
        'performance_issues',
    )

    list_filter = (
        'category',
        'is_verified',
        'is_active',
    )

    search_fields = (
        'name',
        'code',
        'email',
    )

    @admin.display(description='Orders')
    def performance_orders(self, obj):
        from procurement.models import calculate_supplier_performance

        metrics = calculate_supplier_performance(obj)
        return metrics['total_orders']

    @admin.display(description='Fulfilment')
    def performance_fulfilment(self, obj):
        from procurement.models import calculate_supplier_performance

        metrics = calculate_supplier_performance(obj)
        return f"{metrics['fulfilment_rate']:.1f}%"

    @admin.display(description='On-Time')
    def performance_on_time(self, obj):
        from procurement.models import calculate_supplier_performance

        metrics = calculate_supplier_performance(obj)
        return f"{metrics['on_time_delivery_rate']:.1f}%"

    @admin.display(description='Lead Time')
    def performance_lead_time(self, obj):
        from procurement.models import calculate_supplier_performance

        metrics = calculate_supplier_performance(obj)
        return f"{metrics['average_lead_time']:.1f} days"

    @admin.display(description='Issues')
    def performance_issues(self, obj):
        from procurement.models import calculate_supplier_performance

        metrics = calculate_supplier_performance(obj)
        return f"{metrics['issue_rate']:.1f}%"

    

@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = (
        'supplier',
        'product',
        'current_price',
        'previous_price_display',
        'price_change_display',
        'price_change_percentage_display',
        'minimum_quantity',
        'is_active',
    )

    list_filter = ('is_active',)
    search_fields = (
        'supplier__name',
        'product__name',
    )

    @admin.display(description='Previous Price')
    def previous_price_display(self, obj):
        metrics = calculate_price_intelligence(obj)
        previous_price = metrics['previous_price']

        if previous_price is None:
            return 'No history'

        return f"₦{previous_price:,.2f}"

    @admin.display(description='Price Change')
    def price_change_display(self, obj):
        metrics = calculate_price_intelligence(obj)
        change = metrics['price_change']
        return f"₦{change:,.2f}"

    @admin.display(description='Price Change %')
    def price_change_percentage_display(self, obj):
        metrics = calculate_price_intelligence(obj)
        percentage = metrics['price_change_percentage']
        return f"{percentage:.2f}%"


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'supplier_product',
        'price',
        'recorded_at',
        'source',
    )

    search_fields = (
        'supplier_product__supplier__name',
        'supplier_product__product__name',
    )