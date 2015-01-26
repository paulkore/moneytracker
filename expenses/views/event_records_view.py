from decimal import Decimal
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views import generic
from expenses.models import Event, Participant
from django.template.defaulttags import register


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

        self.url_edit = reverse('expenses:money-record-edit',
                                kwargs={'event_name_slug': money_record.event.name_slug, 'record_id': money_record.id})


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def money_amount(decimal_amount):
    if decimal_amount >= 0:
        return "${0:.2f}".format(decimal_amount)
    else:
        return "(${0:.2f})".format(-decimal_amount)


@register.filter
def money_amount_hide_zero(decimal_amount):
    if not decimal_amount:
        return '--'
    else:
        return money_amount(decimal_amount)


class EventRecordsView(generic.TemplateView):
    template_name = "expenses/event_records.html"

    def get_context_data(self, **kwargs):
        context = super(EventRecordsView, self).get_context_data(**kwargs)

        # if not self.request.user.is_authenticated():
        #     return HttpResponseRedirect(reverse('expenses:login'))
            # pass

        event_name_slug = kwargs['event_name_slug']
        event = Event.find_by_name_slug(event_name_slug)

        participants = event.participants()
        money_records = event.money_records()

        participant = None
        for p in participants:
            if p.user_id == self.request.user.id:
                participant = p
                break
        assert participant

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

        context.update({
            'page_title': None, #event.name,
            'event': event,
            'participant_name': participant.get_name(),
            'participants': participants,
            'money_records': money_record_items,
            'event_total': event_total,
            'event_split': event_split,
            'participant_total': participant_total,
            'participant_variance': participant_variance,
            'url_add_record': reverse('expenses:money-record-create', kwargs={'event_name_slug': event_name_slug}),
            'url_logout': reverse('expenses:logout'),
        })

        return context