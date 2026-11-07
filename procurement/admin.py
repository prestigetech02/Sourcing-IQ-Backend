from django.contrib import admin
from .models import Delivery
from .models import GoodsReceiptItem


from .models import PurchaseRequest, PurchaseRequestItem


class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItem
    extra = 1


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = (
        'request_number',
        'organization',
        'requester',
        'required_date',
        'priority',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'organization',
    )

    search_fields = (
        'request_number',
        'requester__username',
    )

    inlines = [PurchaseRequestItemInline]


@admin.register(PurchaseRequestItem)
class PurchaseRequestItemAdmin(admin.ModelAdmin):
    list_display = (
        'purchase_request',
        'product',
        'quantity',
    )

    search_fields = (
        'purchase_request__request_number',
        'product__name',
    )


# from .models import (
#     PurchaseRequest,
#     PurchaseRequestItem,
#     RFQ,
#     RFQSupplier,
#     Quote,
#     QuoteItem,
# )
from django.contrib import admin
from django.template.response import TemplateResponse

from .models import (
    GoodsReceiptItem,
    PurchaseRequest,
    PurchaseRequestItem,
    RFQ,
    RFQSupplier,
    Quote,
    QuoteItem,
    PurchaseOrder,
    PurchaseOrderItem,
    Delivery,
    GoodsReceipt,
    compare_supplier_quotes,
)

class RFQSupplierInline(admin.TabularInline):
    model = RFQSupplier
    extra = 1


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    readonly_fields = ('estimated_total_display',)

    fields = (
        'product',
        'quantity',
        'unit_price',
        'delivery_fee',
        'other_charges',
        'discount',
        'estimated_total_display',
    )

    @admin.display(description='Estimated Total (₦)')
    def estimated_total_display(self, obj):
        if obj and obj.pk:
            return f"₦{obj.estimated_total():,.2f}"
        return "Save item to calculate"


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = (
        'rfq_number',
        'purchase_request',
        'deadline',
        'status',
        'created_by',
        'created_at',
    )

    list_filter = (
        'status',
        'organization',
    )

    search_fields = (
        'rfq_number',
        'purchase_request__request_number',
    )

    inlines = [RFQSupplierInline]

    actions = ['compare_supplier_quotes_action']

    @admin.action(description='Compare supplier quotes for selected RFQs')
    def compare_supplier_quotes_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                'Please select exactly one RFQ to compare its quotes.',
                level='warning',
            )
            return None

        rfq = queryset.first()
        results = compare_supplier_quotes(rfq)

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': f'Quote comparison: {rfq.rfq_number}',
            'rfq': rfq,
            'results': results,
        }

        return TemplateResponse(
            request,
            'admin/procurement/rfq_quote_comparison.html',
            context,
        )

@admin.register(RFQSupplier)
class RFQSupplierAdmin(admin.ModelAdmin):
    list_display = (
        'rfq',
        'supplier',
        'responded',
        'invited_at',
    )

    list_filter = ('responded',)

    search_fields = (
        'rfq__rfq_number',
        'supplier__name',
    )


from decimal import Decimal


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        'quote_number',
        'rfq',
        'supplier',
        'total_estimated_cost',
        'valid_until',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'supplier',
        'rfq',
    )

    search_fields = (
        'quote_number',
        'supplier__name',
        'rfq__rfq_number',
    )

    inlines = [QuoteItemInline]

    @admin.display(description='Total Estimated Cost (₦)')
    def total_estimated_cost(self, obj):
        total = sum(
            (
                item.estimated_total()
                for item in obj.items.all()
            ),
            Decimal('0.00'),
        )
        return f"₦{total:,.2f}"


    

@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = (
        'quote',
        'product',
        'quantity',
        'unit_price',
        'delivery_fee',
        'discount',
    )

    search_fields = (
        'quote__quote_number',
        'product__name',
    )



@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'purchase_order',
        'dispatch_date',
        'expected_delivery_date',
        'actual_delivery_date',
        'delivery_status',
    )

    list_filter = (
        'delivery_status',
        'expected_delivery_date',
        'actual_delivery_date',
    )

    search_fields = (
        'purchase_order__po_number',
        'notes',
    )

class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 1

@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'delivery',
        'received_date',
        'quantity_received',
        'has_issues',
        'received_by',
    )

    list_filter = (
        'has_issues',
        'received_date',
    )

    search_fields = (
        'delivery__purchase_order__po_number',
        'issue_description',
        'received_by__username',
    )
    inlines = [GoodsReceiptItemInline]


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        'po_number',
        'organization',
        'supplier',
        'expected_delivery_date',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'organization',
        'expected_delivery_date',
    )

    search_fields = (
        'po_number',
        'supplier__name',
    )

    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'purchase_order',
        'product',
        'quantity',
        'unit_price',
    )

    search_fields = (
        'purchase_order__po_number',
        'product__name',
    )