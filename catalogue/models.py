from django.db import models
from organizations.models import Organization

class Category(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
# class Category(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name


    
class Product(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=255)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )

    unit = models.CharField(max_length=50)
    specification = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     category = models.ForeignKey(
#         Category,
#         on_delete=models.PROTECT,
#         related_name='products'
#     )
#     unit = models.CharField(max_length=50)
#     specification = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name    
    



# class Supplier(models.Model):
#     name = models.CharField(max_length=255)
#     code = models.CharField(max_length=50, unique=True)

#     category = models.ForeignKey(
#         Category,
#         on_delete=models.PROTECT,
#         related_name='suppliers'
#     )

#     location = models.CharField(max_length=255)
#     delivery_areas = models.TextField(blank=True)

#     email = models.EmailField(blank=True)
#     phone = models.CharField(max_length=20, blank=True)

#     minimum_order_quantity = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         null=True,
#         blank=True
#     )

#     typical_lead_time = models.PositiveIntegerField(
#         help_text="Typical delivery time in days",
#         null=True,
#         blank=True
#     )

#     payment_terms = models.CharField(
#         max_length=255,
#         blank=True
#     )

#     is_verified = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)

#     internal_notes = models.TextField(blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name
    
class Supplier(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='suppliers'
    )

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='suppliers'
    )

    location = models.CharField(max_length=255)
    delivery_areas = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    minimum_order_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    typical_lead_time = models.PositiveIntegerField(
        help_text="Typical delivery time in days",
        null=True,
        blank=True
    )

    payment_terms = models.CharField(
        max_length=255,
        blank=True
    )

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    internal_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SupplierProduct(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='supplier_products'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='supplier_products'
    )

    current_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    minimum_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier', 'product'],
                name='unique_supplier_product'
            )
        ]

    def __str__(self):
        return f"{self.supplier.name} - {self.product.name}"
    


class PriceHistory(models.Model):
    supplier_product = models.ForeignKey(
        SupplierProduct,
        on_delete=models.CASCADE,
        related_name='price_history'
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True
    )

    source = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return (
            f"{self.supplier_product} - "
            f"{self.price}"
        ) 



def calculate_price_intelligence(supplier_product):
    """
    Calculate price intelligence for a supplier product.
    """

    price_history = supplier_product.price_history.all()

    current_price = supplier_product.current_price

    historical_prices = [
        history.price
        for history in price_history
    ]

    all_prices = historical_prices + [current_price]

    lowest_price = min(all_prices)
    highest_price = max(all_prices)
    average_price = sum(all_prices) / len(all_prices)
    previous_price = None

    if price_history.exists():
        previous_price = (
            price_history
            .order_by('-recorded_at')
            .first()
            .price
        )

    price_change = 0
    price_change_percentage = 0

    if previous_price is not None:
        price_change = current_price - previous_price

        if previous_price > 0:
            price_change_percentage = (
                price_change
                / previous_price
            ) * 100

    return {
        'current_price': current_price,
        'previous_price': previous_price,
        'price_change': price_change,
        'price_change_percentage': price_change_percentage,
        'lowest_price': lowest_price,
        'highest_price': highest_price,
        'average_price': average_price,
        'history_count': len(historical_prices),
    }



