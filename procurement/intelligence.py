from decimal import Decimal


def calculate_average_historical_price(supplier_product):
    """
    Calculate the supplier's average historical price
    for a particular product.
    """

    prices = supplier_product.price_history.values_list(
        'price',
        flat=True
    )

    if not prices:
        return None

    total = sum(prices, Decimal('0'))

    return total / len(prices)


def calculate_price_variance(current_price, historical_average):
    """
    Calculate percentage difference between
    current price and historical average.
    """

    if historical_average is None:
        return None

    if historical_average == 0:
        return None

    variance = (
        (current_price - historical_average)
        / historical_average
    ) * 100

    return variance


def price_intelligence(current_price, historical_average):
    """
    Produce a simple explanation of the current price.
    """

    if historical_average is None:
        return {
            'status': 'insufficient_data',
            'message': 'No historical price data available.'
        }

    variance = calculate_price_variance(
        current_price,
        historical_average
    )

    if variance > 10:
        return {
            'status': 'price_increase',
            'variance_percentage': round(variance, 2),
            'message': 'Current price is materially above historical average.'
        }

    if variance < -10:
        return {
            'status': 'price_decrease',
            'variance_percentage': round(variance, 2),
            'message': 'Current price is below historical average.'
        }

    return {
        'status': 'normal',
        'variance_percentage': round(variance, 2),
        'message': 'Current price is within the normal historical range.'
    }    