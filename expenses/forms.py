from decimal import Decimal
from django import forms

from functools import partial
from django.db import transaction

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

from expenses.models import Expense, Contribution, Event, Person, Participant

# class PersonForm(forms.ModelForm):
#     class Meta:
#         model = Person
#         fields = '__all__'


# class PersonForm(forms.Form):
#     name = forms.CharField(label='Name', max_length=50)
#
#     def create_person(self):
#         print('#PersonForm >>> ' + str(self.cleaned_data) )

class ParticipantChoice:

    def __init__(self, participant):
        assert type(participant) is Person
        self.participant = participant

    def choices(self, event):
        choices = []
        for participant in event.participants():
            choices.append(ParticipantChoice(participant))
        return choices


class ExpenseForm(forms.Form):

    pub_date = forms.DateField(label='Date', input_formats = ['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y'], widget=DateInput())
    description = forms.CharField(label='Description', max_length=200)
    amount = forms.DecimalField(label='Amount', decimal_places=2)
    participant = None # initialized dynamically

    def __init__(self, event, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)

        assert type(event) is Event
        # print('Expense form initializing for event: ' + event.name)
        self.event = event
        self.expense = None

        participant_choices=[(None, 'SELECT')]
        for o in event.participant_objects():
            choice = (o.id, str(o.person.name))
            participant_choices.append(choice)

        self.fields['participant'] = forms.ChoiceField(choices=participant_choices)

    def populate_from_object(self, expense):
        assert type(expense) is Expense
        assert expense.event_id is self.event.id

        self.expense = expense
        self.fields['pub_date'].initial = expense.pub_date
        self.fields['description'].initial = expense.description

        contributions = expense.contributions()
        assert len(contributions) is 1, 'Only supporting expenses with a single contribution for now'
        contribution = contributions[0]

        self.fields['amount'].initial = contribution.amount
        self.fields['participant'].initial = contribution.participant_id


    def process(self):
        assert self.is_valid(), 'Assuming that form validation was handled already'

        print('processing ExpenseForm >>> ' + str(self.cleaned_data))

        # TODO: this should wrap the multiple DB writes below in a DB transaction. Verify that it works as expected!
        with transaction.atomic():

            if self.expense :
                print('Updating existing expense (id: %d)' % self.expense.id)
                self._update_existing_expense()

            else :
                print('Creating new expense')
                self._create_new_expense()


    def _update_existing_expense(self):
        assert self.expense
        assert self.expense.event_id is self.event.id

        self.expense.pub_date = self.cleaned_data['pub_date']
        self.expense.description = self.cleaned_data['description']
        self.expense.save()

        contributions = self.expense.contributions()
        assert len(contributions) == 1, 'Only 1 contribution currently supported'
        contribution = contributions[0]

        contribution.participant_id = self.cleaned_data['participant']
        contribution.amount = self.cleaned_data['amount']
        contribution.save()


    def _create_new_expense(self):
        expense = Expense.objects.create(
            event = self.event,
            pub_date = self.cleaned_data['pub_date'],
            description = self.cleaned_data['description'],
        )
        expense.save()

        contribution = Contribution.objects.create(
            expense = expense,
            participant_id = self.cleaned_data['participant'],
            amount = self.cleaned_data['amount'],
        )
        contribution.save()







