from decimal import Decimal
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from moneytracker.auth import has_event_access
from moneytracker.models import Event


class MoneyRecordWrapper:
    def __init__(self, money_record):
        self.record_id = money_record.id
        self.description = money_record.description
        self.pub_date = money_record.pub_date
        self.amount = money_record.amount
        self.participant1 = money_record.participant1
        self.participant2 = money_record.participant2

        assert money_record.participant1
        if money_record.participant2 is None:
            self.contributions = {
                money_record.participant1: self.amount
            }
            self.total_amount = self.amount
        else:
            self.contributions = {
                money_record.participant1: +self.amount,
                money_record.participant2: -self.amount,
            }
            self.total_amount = Decimal(0)

        self.url_edit = reverse('edit-record',
                                kwargs={'event_name_slug': money_record.event.name_slug, 'record_id': money_record.id})


def event_records_view(request, event_name_slug):
        user = request.user
        if not user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))

        event = Event.find_by_name_slug(event_name_slug)
        if not event:
            raise Http404()
        if not has_event_access(user, event):
            raise PermissionDenied()

        participants = event.participants()
        money_records = event.money_records()

        event_total = Decimal(0)
        participant_contribution = {}
        for p in participants:
            participant_contribution[p] = Decimal(0)

        money_record_items = []
        for money_record in money_records:
            money_record_view_item = MoneyRecordWrapper(money_record)
            money_record_items.append(money_record_view_item)
            event_total += money_record_view_item.total_amount
            for p in money_record_view_item.contributions:
                participant_contribution[p] += money_record_view_item.contributions[p]

        event_split = event_total / len(participants)
        participant_variance = {}
        participant_overcontrib = {}
        participant_undercontrib = {}
        for p in participants:
            variance = participant_contribution[p] - event_split
            participant_variance[p] = variance
            if variance > 0:
                participant_overcontrib[p] = variance
            elif variance < 0:
                participant_undercontrib[p] = -variance
            else:
                # zero variance
                pass

        return render(request, 'event_records.html', {
            'event': event,
            'participants': participants,
            'money_records': money_record_items,
            'event_total': event_total,
            'event_split': event_split,
            'participant_contribution': participant_contribution,
            'participant_variance': participant_variance,
            'participant_overcontrib': participant_overcontrib,
            'participant_undercontrib': participant_undercontrib,
            'url_add_expense': reverse('create-expense', kwargs={'event_name_slug': event_name_slug}),
            'url_add_transfer': reverse('create-transfer', kwargs={'event_name_slug': event_name_slug}),
        })
