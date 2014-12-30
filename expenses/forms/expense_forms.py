from decimal import Decimal
from django import forms

from functools import partial
from django.db import transaction

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

from expenses.models import Expense, Contribution, Event, Person, Participant

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

    def __init__(self, event, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)

        assert type(event) is Event
        self.event = event
        self.expense = None

        self.contribution_fields = {}
        for participant in event.participant_objects():
            participant_id = participant.id
            person_name = participant.person.name
            contrib_field_name = 'contribution_par_'+str(participant_id)
            contrib_field_label = 'Contribution - '+person_name
            contrib_field = forms.DecimalField(label=contrib_field_label, decimal_places=2, required=False)
            contrib_field.name = contrib_field_name
            self.fields[contrib_field_name] = contrib_field
            self.contribution_fields[participant_id] = contrib_field


    def _get_contrib_amounts(self):
        d_contrib_amounts = {}
        for participant_id, contrib_field in self.contribution_fields.items():
            contrib_amount = self.cleaned_data[contrib_field.name]
            if contrib_amount and contrib_amount != Decimal(0):
                d_contrib_amounts[participant_id] = contrib_amount

        participants = self.event.participant_objects()
        assert 1 <= len(d_contrib_amounts) <= len(participants)
        return d_contrib_amounts


    def populate_from_object(self, expense):
        assert type(expense) is Expense
        assert expense.event_id is self.event.id

        self.expense = expense
        self.fields['pub_date'].initial = expense.pub_date
        self.fields['description'].initial = expense.description

        contributions = expense.contributions()
        participants = self.event.participant_objects()
        assert 1 <= len(contributions) <= len(participants)
        for contribution in contributions:
            self.contribution_fields[contribution.participant_id].initial = contribution.amount



    def process_save(self):
        assert self.is_valid(), 'Assuming that form validation was handled already'

        with transaction.atomic():
            if self.expense :
                self._update_existing_expense()
            else :
                self._create_new_expense()


    def _update_existing_expense(self):
        assert self.expense
        assert self.expense.event_id is self.event.id

        self.expense.pub_date = self.cleaned_data['pub_date']
        self.expense.description = self.cleaned_data['description']
        self.expense.save()

        contributions = self.expense.contributions()

        participants = self.event.participant_objects()
        assert len(participants) > 0

        d_existing_contrib_records = {}
        for contribution in contributions:
            d_existing_contrib_records[contribution.participant_id] = contribution
        assert 1 <= len(d_existing_contrib_records) <= len(participants)

        d_contrib_amounts = self._get_contrib_amounts()
        assert 1 <= len(d_contrib_amounts) <= len(participants)

        # remove any existing Contribution records, that no longer have an amount
        for participant_id, contrib_record in d_existing_contrib_records.items():
            if participant_id not in d_contrib_amounts:
                contrib_record.delete()

        # apply the contribution amounts from the form
        for participant_id, contrib_amount in d_contrib_amounts.items():

            if participant_id in d_existing_contrib_records:
                # existing Contribution record
                contribution = d_existing_contrib_records[participant_id]
                contribution.amount = contrib_amount
            else:
                # new Contribution record
                contribution = Contribution.objects.create(
                    expense=self.expense,
                    participant_id=participant_id,
                    amount=contrib_amount)
                contribution.save()

        pass


    def _create_new_expense(self):
        expense = Expense.objects.create(
            event = self.event,
            pub_date = self.cleaned_data['pub_date'],
            description = self.cleaned_data['description'],
        )
        expense.save()

        d_contrib_amounts = self._get_contrib_amounts()
        for participant_id, contrib_amount in d_contrib_amounts.items():
            contribution = Contribution.objects.create(
                expense=expense,
                participant_id=participant_id,
                amount=contrib_amount,
            )
            contribution.save()







