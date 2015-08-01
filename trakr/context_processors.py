def default_processor(request):
    responsive_view_toggle = request.COOKIES.get('responsive_view_toggle')

    if responsive_view_toggle is None:
        # cookie not set... responsive behaviour is on by default
        responsive_view_enabled = True

    elif responsive_view_toggle == 'enabled':
        responsive_view_enabled = True

    elif responsive_view_toggle == 'disabled':
        responsive_view_enabled = False

    else:
        raise Exception('Unhandled scenario: ' + str(responsive_view_toggle))

    return {'responsive_view_enabled': responsive_view_enabled}
