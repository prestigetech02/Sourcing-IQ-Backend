from django.db import models
from django.core.validators import MinValueValidator

from accounts.models import User
from catalogue.models import PriceHistory, Product, Supplier
from organizations.models import Organization
from django.db.models import Sum
from django.utils import timezone

# Create your models here.




class PurchaseRequest(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('sourcing', 'Sourcing'),
        ('ordered', 'Ordered'),
        ('partially_fulfilled', 'Partially Fulfilled'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='purchase_requests'
    )

    requester = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='purchase_requests'
    )

    request_number = models.CharField(
        max_length=30,
        unique=True
    )

    required_date = models.DateField()

    specification = models.TextField(blank=True)

    budget_estimate = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    department = models.CharField(
        max_length=100,
        blank=True
    )

    cost_center = models.CharField(
        max_length=100,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.request_number


class PurchaseRequestItem(models.Model):

    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='purchase_request_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    specification = models.TextField(blank=True)

    def __str__(self):
        return f"{self.purchase_request.request_number} - {self.product.name}"



class RFQ(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='rfqs'
    )

    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.PROTECT,
        related_name='rfqs'
    )

    rfq_number = models.CharField(
        max_length=30,
        unique=True
    )

    deadline = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_rfqs'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.rfq_number


class RFQSupplier(models.Model):

    rfq = models.ForeignKey(
        RFQ,
        on_delete=models.CASCADE,
        related_name='invited_suppliers'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='rfq_invitations'
    )

    invited_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['rfq', 'supplier'],
                name='unique_rfq_supplier'
            )
        ]

    def __str__(self):
        return f"{self.rfq.rfq_number} - {self.supplier.name}"


class Quote(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    rfq = models.ForeignKey(
        RFQ,
        on_delete=models.CASCADE,
        related_name='quotes'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='quotes'
    )

    quote_number = models.CharField(
        max_length=30,
        unique=True
    )

    valid_until = models.DateField()

    attachment = models.FileField(
        upload_to='quotations/',
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.quote_number


class QuoteItem(models.Model):

    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='quote_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    delivery_fee = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    other_charges = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    discount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    def estimated_total(self):
        return (
            (self.unit_price * self.quantity)
            + self.delivery_fee
            + self.other_charges
            - self.discount
        )

    def __str__(self):
        return f"{self.quote.quote_number} - {self.product.name}"

    

class PurchaseOrder(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('sent', 'Sent'),
        ('partially_delivered', 'Partially Delivered'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders'
    )

    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        null=True,
        blank=True
    )

    quote = models.ForeignKey(
        Quote,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        null=True,
        blank=True
    )

    po_number = models.CharField(
        max_length=30,
        unique=True
    )

    delivery_location = models.CharField(
        max_length=255
    )

    expected_delivery_date = models.DateField()

    payment_terms = models.CharField(
        max_length=255,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='draft'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.po_number
    

class PurchaseOrderItem(models.Model):

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='purchase_order_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.product.name}"


class Delivery(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    dispatch_date = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)

    delivery_status = models.CharField(
        max_length=30,
        choices=[
            ('pending', 'Pending'),
            ('dispatched', 'Dispatched'),
            ('in_transit', 'In Transit'),
            ('delivered', 'Delivered'),
            ('partially_delivered', 'Partially Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )

    notes = models.TextField(blank=True)
    evidence = models.FileField(
        upload_to='delivery_evidence/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.delivery_status}"




class GoodsReceipt(models.Model):

    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='goods_receipts'
    )

    received_date = models.DateField()

    quantity_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    has_issues = models.BooleanField(default=False)

    issue_description = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    received_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='goods_receipts'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Goods receipt for {self.delivery.purchase_order.po_number} "
            f"- {self.received_date}"
        )




class GoodsReceiptItem(models.Model):

    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name='items'
    )

    purchase_order_item = models.ForeignKey(
        PurchaseOrderItem,
        on_delete=models.PROTECT,
        related_name='goods_receipt_items'
    )

    quantity_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    has_issues = models.BooleanField(default=False)

    issue_description = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    
    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.goods_receipt_id or not self.purchase_order_item_id:
            return

        delivery_purchase_order_id = (
            self.goods_receipt.delivery.purchase_order_id
        )

        item_purchase_order_id = (
            self.purchase_order_item.purchase_order_id
        )

        if delivery_purchase_order_id != item_purchase_order_id:
            raise ValidationError({
                'purchase_order_item': (
                    'This purchase order item does not belong to '
                    'the purchase order associated with this delivery.'
                )
            })


    def __str__(self):
        return (
            f"{self.goods_receipt} - "
            f"{self.purchase_order_item.product.name}"
        )





def calculate_supplier_performance(supplier):
    """
    Calculate supplier performance metrics from purchase orders,
    deliveries, and goods receipts.
    """

    purchase_orders = PurchaseOrder.objects.filter(
        supplier=supplier
    ).exclude(
        status='cancelled'
    )

    total_orders = purchase_orders.count()

    total_order_value = 0
    total_quantity_ordered = 0
    total_quantity_received = 0

    on_time_deliveries = 0
    completed_deliveries = 0

    deliveries = Delivery.objects.filter(
        purchase_order__supplier=supplier
    ).exclude(
        delivery_status='cancelled'
    )

    for purchase_order in purchase_orders:
        for item in purchase_order.items.all():
            total_order_value += item.total_price()
            total_quantity_ordered += item.quantity

    for delivery in deliveries:
        if delivery.actual_delivery_date:
            completed_deliveries += 1

            if (
                delivery.actual_delivery_date
                <= delivery.expected_delivery_date
            ):
                on_time_deliveries += 1

        for receipt in delivery.goods_receipts.all():
            for receipt_item in receipt.items.all():
                total_quantity_received += receipt_item.quantity_received

    fulfilment_rate = 0

    if total_quantity_ordered > 0:
        fulfilment_rate = (
            total_quantity_received
            / total_quantity_ordered
        ) * 100

    on_time_delivery_rate = 0

    if completed_deliveries > 0:
        on_time_delivery_rate = (
            on_time_deliveries
            / completed_deliveries
        ) * 100

    total_lead_time = 0
    lead_time_deliveries = 0

    for delivery in deliveries:
        if (
            delivery.dispatch_date
            and delivery.actual_delivery_date
        ):
            lead_time = (
                delivery.actual_delivery_date
                - delivery.dispatch_date
            ).days

            total_lead_time += lead_time
            lead_time_deliveries += 1

    average_lead_time = 0

    if lead_time_deliveries > 0:
        average_lead_time = (
            total_lead_time
            / lead_time_deliveries
        )

    issue_receipts = GoodsReceipt.objects.filter(
        delivery__purchase_order__supplier=supplier,
        has_issues=True
    ).count()

    total_receipts = GoodsReceipt.objects.filter(
        delivery__purchase_order__supplier=supplier
    ).count()

    issue_rate = 0

    if total_receipts > 0:
        issue_rate = (
            issue_receipts
            / total_receipts
        ) * 100

    average_purchase_value = 0

    if total_orders > 0:
        average_purchase_value = (
            total_order_value
            / total_orders
        )

    return {
        'total_orders': total_orders,
        'total_order_value': total_order_value,
        'average_purchase_value': average_purchase_value,
        'total_quantity_ordered': total_quantity_ordered,
        'total_quantity_received': total_quantity_received,
        'fulfilment_rate': fulfilment_rate,
        'completed_deliveries': completed_deliveries,
        'on_time_deliveries': on_time_deliveries,
        'on_time_delivery_rate': on_time_delivery_rate,
        'average_lead_time': average_lead_time,
        'total_receipts': total_receipts,
        'issue_receipts': issue_receipts,
        'issue_rate': issue_rate,
    }



from decimal import Decimal


def compare_supplier_quotes(rfq):
    """
    Compare supplier quotes for one RFQ.
    Rank submitted quotes by total estimated cost,
    from lowest to highest.
    """
    quotes = (
        Quote.objects
        .filter(rfq=rfq, status='submitted')
        .prefetch_related('items', 'items__product', 'supplier')
    )

    comparison = []

    for quote in quotes:
        items = list(quote.items.all())

        total_cost = sum(
            (item.estimated_total() for item in items),
            Decimal('0.00'),
        )

        comparison.append({
            'quote': quote,
            'supplier': quote.supplier,
            'quote_number': quote.quote_number,
            'total_cost': total_cost,
            'item_count': len(items),
            'is_complete': len(items) > 0,
        })

    comparison.sort(
        key=lambda result: (
            not result['is_complete'],
            result['total_cost'],
        )
    )

    for rank, result in enumerate(comparison, start=1):
        result['rank'] = rank

    return comparison