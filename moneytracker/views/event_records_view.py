from decimal import Decimal
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from moneytracker.models import Event


class MoneyRecordWrapper:
    def __init__(self, money_record):
        self.record_id = money_record.id
        self.description = money_record.description
        self.pub_date = money_record.pub_date

        amount = money_record.amount
        assert money_record.participant1
        if money_record.participant2 is None:
            self.contributions = {
                money_record.participant1: amount
            }
            self.total_amount = amount
        else:
            self.contributions = {
                money_record.participant1: amount,
                money_record.participant2: -amount
            }
            self.total_amount = Decimal(0)

        self.url_edit = reverse('money-record-edit',
                                kwargs={'event_name_slug': money_record.event.name_slug, 'record_id': money_record.id})


def event_records_view(request, event_name_slug):
        user = request.user
        if not user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))

        event = Event.find_by_name_slug(event_name_slug)
        participants = event.participants()
        money_records = event.money_records()

        event_total = Decimal(0)
        participant_total = {}
        for p in participants:
            participant_total[p] = Decimal(0)

        money_record_items = []
        for money_record in money_records:
            money_record_view_item = MoneyRecordWrapper(money_record)
            money_record_items.append(money_record_view_item)
            event_total += money_record_view_item.total_amount
            for p in money_record_view_item.contributions:
                participant_total[p] += money_record_view_item.contributions[p]

        event_split = event_total / len(participants)
        participant_variance = {}
        for p in participants:
            participant_variance[p] = participant_total[p] - event_split

        return render(request, 'event_records.html', {
            'event': event,
            'participants': participants,
            'money_records': money_record_items,
            'event_total': event_total,
            'event_split': event_split,
            'participant_total': participant_total,
            'participant_variance': participant_variance,
            'url_add_record': reverse('money-record-create', kwargs={'event_name_slug': event_name_slug}),

        })
