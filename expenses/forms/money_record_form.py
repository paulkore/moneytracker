from django import forms

from functools import partial
from django.db import transaction

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

from expenses.models import MoneyRecord, Event


class MoneyRecordForm(forms.Form):

    pub_date = forms.DateField(label='Date', input_formats=['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y'], widget=DateInput())
    description = forms.CharField(label='Description', max_length=200)
    amount = forms.DecimalField(label='Amount', decimal_places=2)

    def __init__(self, event, *args, **kwargs):
        super(MoneyRecordForm, self).__init__(*args, **kwargs)

        assert type(event) is Event
        self.event = event
        self.money_record = None

        participant_choices = [(None, '')]
        for participant in event.participants():
            participant_choices.append((participant.id, participant.get_name()))
        self.fields['participant1'] = forms.ChoiceField(
            label='Participant 1', choices=participant_choices, required=True)
        self.fields['participant2'] = forms.ChoiceField(
            label='Participant 2', choices=participant_choices, required=False)

    def populate_from_object(self, money_record):
        assert type(money_record) is MoneyRecord
        assert money_record.event_id is self.event.id

        self.money_record = money_record
        self.fields['pub_date'].initial = money_record.pub_date
        self.fields['description'].initial = money_record.description
        self.fields['amount'].initial = money_record.amount
        self.fields['participant1'].initial = money_record.participant1.id
        self.fields['participant2'].initial = None if not money_record.participant2 else money_record.participant2.id

    # custom validation of fields that depend on each other
    def clean(self):
        cleaned_data = super(MoneyRecordForm, self).clean()
        participant1 = cleaned_data.get('participant1')
        participant2 = cleaned_data.get('participant2')

        if participant1 and participant2 and participant1 == participant2:
            self.add_error('participant2', 'Value must be different from Participant 1')

    def process(self):
        assert self.is_valid(), 'Assuming that form validation was handled already'

        with transaction.atomic():
            if self.money_record:
                # editing an existing record
                assert self.money_record.event_id is self.event.id
                self.money_record.pub_date = self.cleaned_data['pub_date']
                self.money_record.description = self.cleaned_data['description']
                self.money_record.amount = self.cleaned_data['amount']
                self.money_record.participant1_id = self.cleaned_data['participant1']
                self.money_record.participant2_id = self.cleaned_data['participant2']
                self.money_record.save()
            else:
                # create a new record
                money_record = MoneyRecord.objects.create(
                    event=self.event,
                    pub_date=self.cleaned_data['pub_date'],
                    description=self.cleaned_data['description'],
                    amount=self.cleaned_data['amount'],
                    participant1_id=self.cleaned_data['participant1'],
                    participant2_id=self.cleaned_data['participant2'],
                )
                money_record.save()
