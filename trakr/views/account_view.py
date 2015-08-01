from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from trakr.models import Participant


class EventData:
    def __init__(self, participant):
        assert type(participant) is Participant

        event = participant.event
        self.event_name = event.name
        self.event_url = reverse('event-records', kwargs={'event_name_slug': event.name_slug})

        self.participant_name = participant.name
        if not self.participant_name or not self.participant_name.strip():
            self.participant_name = 'N/A'

        self.is_default = participant.is_default
        self.url_make_default = reverse('account-event-make-default', kwargs={'participant_id': participant.id})


def account_view(request):

    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    first_name = user.first_name
    if not first_name or not first_name.strip():
        first_name = 'N/A'

    last_name = user.last_name
    if not last_name or not last_name.strip():
        last_name = 'N/A'

    event_data_objects = []
    participants = Participant.find_by_user(user)
    for participant in participants:
        event_data_objects.append(EventData(participant))

    return render(request, 'account.html', {
        'username': user.username,
        'first_name': first_name,
        'last_name': last_name,
        'event_list': event_data_objects,
    })


def account_event_make_default(request, participant_id):
    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    # confirm that the participant id exists, and belongs to this user
    par_check = Participant.objects.get(id=participant_id)
    if not par_check:
        raise Http404()
    if not par_check.user_id == user.id:
        raise PermissionDenied()

    # apply the change
    with transaction.atomic():
        par_id = int(participant_id)
        for participant in Participant.find_by_user(user):
            if par_id == participant.id:
                participant.is_default = True
                participant.save()
            else:
                participant.is_default = False
                participant.save()

    # return to the account page
    return HttpResponseRedirect(reverse('account'))