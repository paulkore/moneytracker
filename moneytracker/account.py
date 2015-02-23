from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from moneytracker.models import Event


def landing_page_redirect(user):
    # TODO: the landing page should be the following:
    # - the user's account page (default, as this page always exists)
    # - one of the user's events' pages (configurable from the account page)

    events = Event.find_by_user(user)
    if len(events) == 0:
        return HttpResponseRedirect(reverse('account'))

    # for now, the landing page is the newest event that the user is associated with
    landing_event = events.latest('id')
    return HttpResponseRedirect(reverse('event-records', kwargs={'event_name_slug': landing_event.name_slug}))
