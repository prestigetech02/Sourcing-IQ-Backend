from decimal import Decimal


def calculate_on_time_rate(deliveries):
    """
    Percentage of deliveries that arrived
    on or before the expected delivery date.
    """

    total = len(deliveries)

    if total == 0:
        return Decimal('0')

    on_time = sum(
        1 for delivery in deliveries
        if delivery.actual_delivery_date
        and delivery.actual_delivery_date
        <= delivery.expected_delivery_date
    )

    return (
        Decimal(on_time) / Decimal(total)
    ) * Decimal('100')


def calculate_average_lead_time(deliveries):
    """
    Average number of days between order and delivery.
    """

    completed = [
        delivery
        for delivery in deliveries
        if delivery.actual_delivery_date
    ]

    if not completed:
        return Decimal('0')

    total_days = sum(
        (
            delivery.actual_delivery_date
            - delivery.order_date
        ).days
        for delivery in completed
    )

    return (
        Decimal(total_days)
        / Decimal(len(completed))
    )


def calculate_fulfilment_rate(quantity_ordered, quantity_received):
    """
    Percentage of ordered quantity actually received.
    """

    if quantity_ordered == 0:
        return Decimal('0')

    return (
        Decimal(quantity_received)
        / Decimal(quantity_ordered)
    ) * Decimal('100')