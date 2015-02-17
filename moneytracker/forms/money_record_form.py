from django import forms

from functools import partial
from django.db import transaction
from django.http import QueryDict

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

from moneytracker.models import MoneyRecord, Event, Participant


class MoneyRecordForm(forms.Form):

    # field declarations
    date = forms.DateField(label='Date', input_formats=['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y'], widget=DateInput())
    amount = forms.DecimalField(label='Amount', decimal_places=2)
    description = forms.CharField(label='Description', max_length=200)
    participant1 = forms.ChoiceField(label='Paid for expense', choices=[])
    participant2 = forms.ChoiceField(label='N/A', choices=[], required=False)
    record_type_hidden = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, event, *args, **kwargs):
        super(MoneyRecordForm, self).__init__(*args, **kwargs)

        assert type(event) is Event
        self.event = event

        participant_choices = [(None, '')]
        for participant in event.participants():
            participant_choices.append((participant.id, participant.get_name()))
        self.fields['participant1'].choices = participant_choices
        self.fields['participant2'].choices = participant_choices

        # record type: expense (default) or transfer
        self.record_type = 'expense'

        if args and type(args[0]) is QueryDict:
            # the form is populated from POST data
            query_dict = args[0]
            assert 'record_type_hidden' in query_dict, 'Could not find record type in POST data'
            rec_type = query_dict['record_type_hidden']
            self.set_record_type(rec_type)

    def set_record_type(self, record_type):
        assert record_type == 'expense' or record_type == 'transfer', 'Invalid: ' + record_type
        self.record_type = record_type
        self.fields['record_type_hidden'].initial = record_type

        if self.record_type == 'expense':
            self.fields['description'].required = True
            self.fields['description'].label = 'Description'

            self.fields['participant1'].required = True
            self.fields['participant1'].label = 'Paid by:'

            self.fields['participant2'].required = False
            self.fields['participant2'].label = 'N/A'

        elif self.record_type == 'transfer':
            self.fields['description'].required = False
            self.fields['description'].label = 'N/A'

            self.fields['participant1'].required = True
            self.fields['participant1'].label = 'Transfer from'

            self.fields['participant2'].required = True
            self.fields['participant2'].label = 'Transfer to'

        else:
            raise Exception('Invalid: ' + self.record_type)

    def populate_from_record(self, record):
        assert type(record) is MoneyRecord
        assert record.event_id is self.event.id

        assert record.pub_date
        assert record.amount
        assert record.description
        assert record.participant1
        if record.participant2:
            self.set_record_type('transfer')
        else:
            self.set_record_type('expense')

        self.fields['date'].initial = record.pub_date
        self.fields['amount'].initial = record.amount

        if self.record_type == 'expense':
            self.fields['description'].initial = record.description
            self.fields['participant1'].initial = record.participant1.id
            self.fields['participant2'].initial = None

        elif self.record_type == 'transfer':
            self.fields['description'].initial = None
            self.fields['participant1'].initial = record.participant1.id
            self.fields['participant2'].initial = record.participant2.id

        else:
            raise Exception('Invalid: ' + self.record_type)

    # custom validation of fields
    def clean(self):
        cleaned_data = super(MoneyRecordForm, self).clean()

        if self.record_type == 'expense':
            # no custom validation for expenses
            pass

        elif self.record_type == 'transfer':
            participant1_id = cleaned_data.get('participant1')
            participant2_id = cleaned_data.get('participant2')
            if participant1_id and participant2_id:
                if participant1_id == participant2_id:
                    self.add_error('participant1', "Must be different")
                    self.add_error('participant2', "Must be different")
                else:
                    participant1 = Participant.objects.get(pk=participant1_id)
                    participant2 = Participant.objects.get(pk=participant2_id)
                    assert participant1 and participant2
                    cleaned_data['description'] = 'Transfer from ' + participant1.get_name() \
                                                  + ' to ' + participant2.get_name()

        else:
            raise Exception('Invalid: ' + self.record_type)

    def save_as_new_record(self):
        assert self.is_valid(), 'Form validation is a pre-requisite'
        with transaction.atomic():
            new_record = MoneyRecord.objects.create(
                event=self.event,
                pub_date=self.cleaned_data['date'],
                description=self.cleaned_data['description'],
                amount=self.cleaned_data['amount'],
                participant1_id=self.cleaned_data['participant1'],
                participant2_id=self.cleaned_data['participant2'],
            )
            new_record.save()

    def update_existing(self, record):
        assert self.is_valid(), 'Form validation is a pre-requisite to this function'
        assert type(record) is MoneyRecord

        with transaction.atomic():
            assert record.event_id is self.event.id
            record.pub_date = self.cleaned_data['date']
            record.description = self.cleaned_data['description']
            record.amount = self.cleaned_data['amount']
            record.participant1_id = self.cleaned_data['participant1']
            record.participant2_id = self.cleaned_data['participant2']
            record.save()
