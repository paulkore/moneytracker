from django.core.urlresolvers import reverse
from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def money_amount(decimal_amount):
    if decimal_amount >= 0:
        return "${0:.2f}".format(decimal_amount)
    else:
        return "(${0:.2f})".format(-decimal_amount)


@register.filter
def money_amount_hide_zero(decimal_amount):
    if not decimal_amount:
        return '--'
    else:
        return money_amount(decimal_amount)


@register.filter
def user_name(user):
    return user.first_name


