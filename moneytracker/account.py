from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from moneytracker.models import Event


def landing_page_redirect(user):
    # TODO: the landing page should be the following:
    # - the user's account page (default, as this page always exists)
    # - one of the user's events' pages (configurable from the account page)

    # for now, the landing page is the first event that's relevant:
    events = Event.find_by_user(user)
    assert len(events) > 0, 'User "' + user.username + '" must be associated with at least one event'
    return HttpResponseRedirect(reverse('event-records', kwargs={'event_name_slug': events[0].name_slug}))
