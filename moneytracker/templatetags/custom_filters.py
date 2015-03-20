from decimal import Decimal
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def money_amount(decimal_amount, number_format):
    assert number_format in ('no-cents', 'simple', 'finance'), 'unknown format: ' + str(number_format)

    if number_format == 'no-cents':
        if decimal_amount >= 0:
            return "${0:.0f}".format(decimal_amount)
        else:
            return "-${0:.0f}".format(-decimal_amount)

    if number_format == 'simple':
        if decimal_amount >= 0:
            return "${0:.2f}".format(decimal_amount)
        else:
            return "-${0:.2f}".format(-decimal_amount)

    if number_format == 'finance':
        if decimal_amount >= 0:
            return "${0:.2f}".format(decimal_amount)
        else:
            return "(${0:.2f})".format(-decimal_amount)

    # shouldn't reach this line
    raise Exception('logic error')


@register.filter
def money_amount_hide_zero(decimal_amount, number_format):
    if not decimal_amount:
        return '--'

    return money_amount(decimal_amount, number_format)


@register.filter
def user_name(user):
    if not user.first_name or not user.first_name.strip():
        return user.username
    else:
        return user.first_name


