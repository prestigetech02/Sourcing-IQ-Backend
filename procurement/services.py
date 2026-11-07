from decimal import Decimal

from .intelligence import price_intelligence


def calculate_quote_item_total(quote_item):

    return (
        (quote_item.unit_price * quote_item.quantity)
        + quote_item.delivery_fee
        + quote_item.other_charges
        - quote_item.discount
    )


def compare_quotes(rfq):

    results = []

    quotes = (
        rfq.quotes
        .filter(status='submitted')
        .select_related('supplier')
        .prefetch_related(
            'items',
            'items__product',
            'items__product__supplier_products',
            'items__product__supplier_products__price_history',
        )
    )

    for quote in quotes:

        total_cost = Decimal('0')
        unit_price_total = Decimal('0')
        intelligence = []

        for item in quote.items.all():

            unit_price_total += (
                item.unit_price * item.quantity
            )

            total_cost += calculate_quote_item_total(item)

            supplier_product = (
                item.product
                .supplier_products
                .filter(
                    supplier=quote.supplier
                )
                .first()
            )

            if supplier_product:

                historical_average = (
                    supplier_product.price_history
                    .all()
                )

                prices = [
                    history.price
                    for history in historical_average
                ]

                if prices:

                    average_price = (
                        sum(prices, Decimal('0'))
                        / len(prices)
                    )

                    intelligence.append({
                        'product': item.product.name,
                        'current_price': item.unit_price,
                        'historical_average': average_price,
                        'price_analysis': price_intelligence(
                            item.unit_price,
                            average_price
                        ),
                    })

        results.append({
            'quote_id': quote.id,
            'quote_number': quote.quote_number,
            'supplier': quote.supplier.name,
            'unit_price_total': unit_price_total,
            'estimated_total': total_cost,
            'valid_until': quote.valid_until,
            'intelligence': intelligence,
        })

    results.sort(
        key=lambda quote: quote['estimated_total']
    )

    return results