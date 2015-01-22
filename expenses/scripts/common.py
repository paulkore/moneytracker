def str_date(datetime):
    return datetime.strftime('%Y-%m-%d')


def str_datetime(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')


def str_money(amount):
    return "${0:.2f}".format(amount)


def str_q(str):
    return '\"' + str + '\"'
