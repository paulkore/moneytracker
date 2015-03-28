from decimal import Decimal
from django import forms

from functools import partial
from django.db import transaction
from django.http import QueryDict

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

from moneytracker.models import MoneyRecord, Event, Participant, Allocation, MoneyRecordType, AllocationType


class MoneyRecordForm(forms.Form):

    # field declarations
    record_type_hidden = forms.CharField(widget=forms.HiddenInput())

    date = forms.DateField(label='Date',
                           input_formats=['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y'],
                           widget=DateInput(),
                           required=True)

    amount = forms.DecimalField(label='Amount', decimal_places=2, required=True)

    description = forms.CharField(label='Description', max_length=200, required=True)

    participant1 = forms.ChoiceField(label='Paid for expense',
                                     choices=[(None, '')],
                                     required=True)

    participant2 = forms.ChoiceField(label='N/A',
                                     choices=[(None, '')],
                                     required=False)

    allocations_toggle = forms.ChoiceField(label='Shared by',
                                           choices=[
                                               (0, 'Everyone (equal amounts)'),
                                               (1, 'Select (equal amounts)'),
                                               (2, 'Custom amounts'),
                                           ],
                                           initial=0,
                                           required=True)

    allocations = forms.MultipleChoiceField(label='Allocations',
                                            choices=[],
                                            required=False,
                                            widget=forms.CheckboxSelectMultiple())

    def __init__(self, event, *args, **kwargs):
        super(MoneyRecordForm, self).__init__(*args, **kwargs)

        assert type(event) is Event
        self.event = event

        participant_choices = []
        self._event_participant_ids = []
        participants = event.participants()
        for participant in participants:
            participant_choices.append((participant.id, participant.get_name()))
            self._event_participant_ids.append(participant.id)

        self.fields['participant1'].choices += participant_choices
        self.fields['participant2'].choices += participant_choices
        self.fields['allocations'].choices += participant_choices
        self.fields['allocations'].initial = self._event_participant_ids

        self._custom_amount_fields = []
        self._custom_amount_fields_by_field_name = {}
        self._custom_amount_fields_by_participant_id = {}

        for participant in participants:
            field = forms.DecimalField(
                label=participant.get_name(),
                decimal_places=2,
                required=False,
                initial=None,
            )
            # using participant id in the field name to guarantee uniqueness
            field_name = 'custom_amount_par_' + str(participant.id)
            field.participant_id = participant.id

            self.fields[field_name] = field
            self._custom_amount_fields.append(field)
            self._custom_amount_fields_by_field_name[field_name] = field
            self._custom_amount_fields_by_participant_id[participant.id] = field

        # 'expense' or 'transfer'; set by set_record_type() method
        self.record_type = None

        if args and type(args[0]) is QueryDict:
            # the form is populated from POST data
            query_dict = args[0]
            assert 'record_type_hidden' in query_dict, 'Could not find record type in POST data'
            rec_type = query_dict['record_type_hidden']
            self.set_record_type(rec_type)

    def custom_amount_fields(self):
        for name in self.fields:
            if name.startswith('custom_amount_par_'):
                yield(self[name])

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

            self.fields['allocations_toggle'].required = False
            self.fields['allocations_toggle'].label = 'N/A'

            self.fields['allocations'].required = False
            self.fields['allocations'].label = 'N/A'

        else:
            raise Exception('Invalid: ' + self.record_type)

    def populate_from_record(self, money_record):
        assert type(money_record) is MoneyRecord
        assert money_record.event_id is self.event.id

        if money_record.type == MoneyRecordType.EXPENSE:
            self.set_record_type('expense')
        elif money_record.type == MoneyRecordType.TRANSFER:
            self.set_record_type('transfer')
        else:
            raise Exception('Unhandled enum value')

        self.fields['date'].initial = money_record.pub_date
        self.fields['amount'].initial = money_record.amount

        if self.record_type == 'expense':
            self.fields['description'].initial = money_record.description
            self.fields['participant1'].initial = money_record.participant1.id
            self.fields['participant2'].initial = None

            allocations = money_record.allocations()
            allocation_type = money_record.allocation_type()
            allocation_participant_ids = []
            allocation_amounts = {}
            for allocation in allocations:
                allocation_participant_ids.append(allocation.participant_id)
                allocation_amounts[allocation.participant_id] = allocation.amount

            if allocation_type == AllocationType.EQUAL:
                equal_amount = money_record.equal_allocation_amount()

                if len(self._event_participant_ids) == len(allocations):
                    # everyone, equal amounts
                    self.fields['allocations_toggle'].initial = 0
                    self.fields['allocations'].initial = self._event_participant_ids
                    for field in self._custom_amount_fields:
                        field.initial = equal_amount

                else:
                    # not everyone, equal amounts
                    self.fields['allocations_toggle'].initial = 1
                    self.fields['allocations'].initial = allocation_participant_ids
                    for participant_id in allocation_amounts:
                        self._custom_amount_fields_by_participant_id[participant_id].initial = equal_amount

            elif allocation_type == AllocationType.CUSTOM:
                # custom amounts
                self.fields['allocations_toggle'].initial = 2
                self.fields['allocations'].initial = allocation_participant_ids
                for participant_id in allocation_amounts:
                    self._custom_amount_fields_by_participant_id[participant_id].initial = allocation_amounts[participant_id]

            else:
                raise Exception('Unhandled enum value')

        elif self.record_type == 'transfer':
            self.fields['description'].initial = None
            self.fields['participant1'].initial = money_record.participant1.id
            self.fields['participant2'].initial = money_record.participant2.id

        else:
            raise Exception('Invalid: ' + str(self.record_type))

    # custom validation of fields
    def clean(self):
        cleaned_data = super(MoneyRecordForm, self).clean()



        if self.record_type == 'expense':

            expense_amount = cleaned_data.get('amount')
            if expense_amount and expense_amount == 0:
                self.add_error('amount', 'Must be non-zero')

            allocations_toggle = self.cleaned_data['allocations_toggle']
            assert allocations_toggle in ('0', '1', '2')

            if allocations_toggle == '1':
                # equal allocation amounts
                allocations = cleaned_data.get('allocations')
                if len(allocations) < 1:
                    self.add_error('allocations', 'Must select at least one')

            if allocations_toggle == '2':
                # custom allocation amounts
                if expense_amount:
                    custom_amount_total = Decimal(0)
                    for field_name in self._custom_amount_fields_by_field_name:
                        custom_amount = cleaned_data.get(field_name)
                        if custom_amount:
                            custom_amount_total += custom_amount
                    delta = custom_amount_total - expense_amount
                    if abs(delta) > 0.01:
                        error_msg = 'These must add up to ' + str(expense_amount)
                        if delta > 0:
                            error_msg += ' (over by ' + str(abs(delta)) + ')'
                        else:
                            error_msg += ' (under by ' + str(abs(delta)) + ')'

                        self.add_error('allocations_toggle', error_msg)
                else:
                    self.add_error('allocations_toggle', 'These must add up to equal the Amount value')

        elif self.record_type == 'transfer':
            participant1_id = cleaned_data.get('participant1')
            participant2_id = cleaned_data.get('participant2')
            if participant1_id and participant2_id:
                if participant1_id == participant2_id:
                    self.add_error('participant1', 'Must be different from the choice below')
                    self.add_error('participant2', 'Must be different from the choice above')
                else:
                    participant1 = Participant.objects.get(pk=participant1_id)
                    participant2 = Participant.objects.get(pk=participant2_id)
                    assert participant1 and participant2
                    cleaned_data['description'] = 'Transfer of funds'

        else:
            raise Exception('Invalid: ' + str(self.record_type))

    def _get_allocations(self):
        assert self.record_type == 'expense', 'Unsupported operation'

        allocations_toggle = self.cleaned_data['allocations_toggle']
        assert allocations_toggle

        allocations = {}

        if allocations_toggle == '0':
            allocation_type = AllocationType.EQUAL
            for participant_id in self._event_participant_ids:
                allocations[participant_id] = None

        elif allocations_toggle == '1':
            allocation_type = AllocationType.EQUAL
            for participant_id in self.cleaned_data['allocations']:
                allocations[participant_id] = None

        elif allocations_toggle == '2':
            allocation_type = AllocationType.CUSTOM
            for field_name in self._custom_amount_fields_by_field_name:
                field = self._custom_amount_fields_by_field_name[field_name]
                custom_amount = self.cleaned_data[field_name]
                if custom_amount and custom_amount != 0:
                    allocations[field.participant_id] = custom_amount

        else:
            raise Exception('Unhandled value: ' + str(allocations_toggle))

        return allocation_type, allocations

    def save_as_new_record(self):
        assert self.is_valid(), 'Form validation is a pre-requisite'

        with transaction.atomic():
            new_record = MoneyRecord.objects.create(
                event=self.event,
                pub_date=self.cleaned_data['date'],
                description=self.cleaned_data['description'],
                amount=self.cleaned_data['amount'],
                type=MoneyRecordType.from_string(self.record_type),
                participant1_id=self.cleaned_data['participant1'],
                participant2_id=self.cleaned_data['participant2'],
            )
            new_record.save()

            if self.record_type == 'expense':
                # Create allocations for expense record

                allocation_type, allocations = self._get_allocations()
                assert len(allocations) > 0

                for participant_id in allocations:
                    new_allocation = Allocation.objects.create(
                        money_record=new_record,
                        participant_id=participant_id,
                        type=allocation_type,
                        amount=allocations[participant_id],
                    )
                    new_allocation.save()

        pass

    def update_existing(self, money_record):
        assert self.is_valid(), 'Form validation is a pre-requisite to this function'
        assert type(money_record) is MoneyRecord
        assert money_record.type == MoneyRecordType.from_string(self.record_type), 'record type assumed to be constant'

        with transaction.atomic():
            assert money_record.event_id is self.event.id
            money_record.pub_date = self.cleaned_data['date']
            money_record.description = self.cleaned_data['description']
            money_record.amount = self.cleaned_data['amount']
            money_record.participant1_id = self.cleaned_data['participant1']
            money_record.participant2_id = self.cleaned_data['participant2']
            money_record.save()

            if self.record_type == 'expense':
                # deal with allocations for expense record

                allocation_type, allocations = self._get_allocations()
                assert len(allocations) > 0

                # delete existing allocations that no longer hold, and update modified fields
                existing_allocations = money_record.allocations()
                for existing_allocation in existing_allocations:
                    if existing_allocation.participant_id in allocations:
                        amount = allocations.pop(existing_allocation.participant_id)
                        existing_allocation.type = allocation_type
                        existing_allocation.amount = amount
                        existing_allocation.save()
                    else:
                        existing_allocation.delete()

                # add new allocations that do not exist yet (the ones that remain in the dictionary)
                for participant_id in allocations:
                    new_allocation = Allocation.objects.create(
                        money_record=money_record,
                        participant_id=participant_id,
                        type=allocation_type,
                        amount=allocations[participant_id],
                    )
                    new_allocation.save()

        pass
