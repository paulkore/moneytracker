from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from moneytracker.models import Participant


def landing_page_redirect(user):

    participants = Participant.find_by_user(user)
    if len(participants) == 0:
        # user does not partake in any events
        return HttpResponseRedirect(reverse('account'))

    default = []
    for participant in participants:
        if participant.is_default:
            default.append(participant)

    if len(default) == 0:
        # user has not designated any event as 'default'
        # redirect to the user account page
        return HttpResponseRedirect(reverse('account'))

    if len(default) > 1:
        # user has more than 1 'default' event designations.
        # reset, and redirect to the user account page
        with transaction.atomic():
            for p in default:
                p.is_default = False
                p.save()

        return HttpResponseRedirect(reverse('account'))

    default_event = default[0].event
    return HttpResponseRedirect(reverse('event-records', kwargs={'event_name_slug': default_event.name_slug}))
