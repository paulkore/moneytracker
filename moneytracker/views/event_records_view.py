from decimal import Decimal
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from moneytracker.auth import has_event_access
from moneytracker.models import Event, MoneyRecord, Participant, MoneyRecordType


class MoneyRecordData:
    def __init__(self, money_record):
        assert type(money_record) is MoneyRecord

        self.record_id = money_record.id
        self.date = money_record.pub_date
        self.description = money_record.description
        self.amount = money_record.amount
        self.participant1 = money_record.participant1
        self.participant2 = money_record.participant2

        self.contributions = {}
        self.expense_allocations = {}

        if money_record.type == MoneyRecordType.EXPENSE:
            self.type = 'expense'

            self.amount_towards_total = self.amount
            self.contributions[money_record.participant1] = self.amount

            allocations = money_record.allocations()
            assert len(allocations) > 0
            allocation_amount = self.amount / len(allocations)
            for allocation in allocations:
                self.expense_allocations[allocation.participant] = allocation_amount

        elif money_record.type == MoneyRecordType.TRANSFER:
            self.type = 'transfer'

            self.amount_towards_total = Decimal(0)
            self.contributions[money_record.participant1] = +self.amount
            self.contributions[money_record.participant2] = -self.amount

        else:
            raise Exception('Unhandled enum value')

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
        money_records = event.money_records().reverse()

        event_total = Decimal(0)

        participant_contribution = {}
        participant_expense_allocation = {}
        for p in participants:
            participant_contribution[p] = Decimal(0)
            participant_expense_allocation[p] = Decimal(0)

        money_record_data_items = []
        for money_record in money_records:
            money_record_data = MoneyRecordData(money_record)
            money_record_data_items.append(money_record_data)
            event_total += money_record_data.amount_towards_total
            for p in money_record_data.contributions:
                participant_contribution[p] += money_record_data.contributions[p]
            for p in money_record_data.expense_allocations:
                participant_expense_allocation[p] += money_record_data.expense_allocations[p]

        participant_variance = {}
        participant_overcontrib = {}
        participant_undercontrib = {}
        for p in participants:
            variance = participant_contribution[p] - participant_expense_allocation[p]
            participant_variance[p] = variance
            if variance > 0:
                participant_overcontrib[p] = variance
            elif variance < 0:
                participant_undercontrib[p] = abs(variance)
            else:
                # zero variance
                pass

        url_add_expense = reverse('create-expense', kwargs={'event_name_slug': event_name_slug})
        url_add_transfer = reverse('create-transfer', kwargs={'event_name_slug': event_name_slug})

        return render(request, 'event_records.html', {
            'event': event,
            'participants': participants,
            'money_records': money_record_data_items,
            'event_total': event_total,
            'participant_contribution': participant_contribution,
            'participant_expense_allocation': participant_expense_allocation,
            'participant_variance': participant_variance,
            'participant_overcontrib': participant_overcontrib,
            'participant_undercontrib': participant_undercontrib,
            'url_add_expense': url_add_expense,
            'url_add_transfer': url_add_transfer,
            'mobile_actions': [
                MobileAction(display_name='record an expense', url=url_add_expense),
                MobileAction(display_name='record a transfer', url=url_add_transfer),
            ]
        })


class MobileAction:
    def __init__(self, display_name, url):
        assert type(display_name) is str
        assert type(url) is str

        self.display_name = display_name
        self.url = url
