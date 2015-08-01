from decimal import Decimal


def round_to_dollar(money_amount):
    remainder = money_amount.remainder_near(Decimal('1.00'))
    if remainder == Decimal('0.50'):
        # flip the sign so that 0.50 rounds up, not down
        remainder *= -1

    result = money_amount - remainder
    return result.quantize(Decimal('0.00'))
