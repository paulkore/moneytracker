from decimal import Decimal
from django.core.urlresolvers import reverse
from django.views import generic
from expenses.models import Event
from django.template.defaulttags import register


class ExpenseObject:
    def __init__(self, expense, participants):
        self.expense_id = expense.id
        self.description = expense.description
        self.pub_date = expense.pub_date
        self.total_amount = expense.total_amount()
        self.contributions = {}
        d_contributions = expense.contributions_dict()
        for person in participants:
            contribution = Decimal(0)
            if person in d_contributions:
                contribution = d_contributions[person]
            self.contributions[person] = contribution

        self.url_edit = reverse('expenses:event-expense-edit', kwargs={'event_name_slug': expense.event.name_slug, 'expense_id': expense.id})
        self.url_delete = reverse('expenses:event-expense-delete', kwargs={'event_name_slug': expense.event.name_slug, 'expense_id': expense.id})

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def money_amount(decimal_amount):
    return money_amount_str(decimal_amount)

@register.filter
def money_amount_hide_zero(decimal_amount):
    if not decimal_amount:
        return '--'
    else:
        return money_amount(decimal_amount)

def money_amount_str(amount):
    if amount >= 0:
        return "${0:.2f}".format(amount)
    else:
        return "(${0:.2f})".format(-amount)





class EventExpensesView(generic.TemplateView):
    template_name = "expenses/event_expenses.html"

    def get_context_data(self, **kwargs):
        context = super(EventExpensesView, self).get_context_data(**kwargs)

        event_name_slug = kwargs['event_name_slug']
        event = Event.find_by_name_slug(event_name_slug)

        participants = event.participants()
        expenses = event.expenses()

        event_total = Decimal(0)
        participant_total = {}
        for person in participants:
            participant_total[person] = Decimal(0)

        expense_objects = []
        for expense in expenses:
            expense_object = ExpenseObject(expense, participants)
            expense_objects.append(expense_object)
            event_total += expense_object.total_amount
            for person in participants:
                participant_total[person] += expense_object.contributions[person]

        event_split = event_total / len(participants)
        participant_variance = {}
        for person in participants:
            participant_variance[person] = participant_total[person] - event_split

        context.update({
            'event': event,
            'participants': participants,
            'expenses_list': expense_objects,
            'event_total': event_total,
            'event_split': event_split,
            'participant_total': participant_total,
            'participant_variance': participant_variance,
            'url_add_expense': reverse('expenses:event-expense-create', kwargs={'event_name_slug': event_name_slug})
        })

        return context