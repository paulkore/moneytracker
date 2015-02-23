from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from moneytracker.models import Participant, Event


class EventData:
    def __init__(self, participant):
        assert type(participant) is Participant

        event = participant.event
        self.event_name = event.name
        self.event_url = reverse('event-records', kwargs={'event_name_slug': event.name_slug})

        self.participant_name = participant.name
        if not self.participant_name or not self.participant_name.strip():
            self.participant_name = 'N/A'


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
