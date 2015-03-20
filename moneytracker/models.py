from decimal import Decimal, ROUND_DOWN
from django.contrib.auth.models import User
from django.db import models, transaction
from django.template.defaultfilters import slugify

from django_enumfield import enum


class Event(models.Model):
    name = models.CharField(max_length=100)
    name_slug = models.SlugField(max_length=100, default='this-value-is-auto-generated')

    class Meta:
        db_table = 'mt_event'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)

    def participants(self):
        return Participant.objects.filter(event_id=self.id).order_by('id')

    def money_records(self):
        return MoneyRecord.objects.filter(event_id=self.id).order_by('pub_date', 'id')

    @staticmethod
    def find_by_name_slug(name_slug):
        assert type(name_slug) is str
        results = Event.objects.filter(name_slug=name_slug)
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]
        else:
            raise Exception('Unexpected: more than one event found by name slug: ' + name_slug)

    @staticmethod
    def find_by_user(user):
        event_ids = set()
        participants = Participant.find_by_user(user)
        for participant in participants:
            event_ids.add(participant.event_id)
        events = Event.objects.filter(id__in=event_ids).order_by('id')
        return events


class Participant(models.Model):
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=15, blank=False, null=True)
    is_default = models.BooleanField(blank=False, null=False, default=False)

    class Meta:
        db_table = 'mt_participant'

    def __str__(self):
        return "{0} - {1}".format(self.event.name, self.get_name())

    # @return The local name value if one is set, otherwise falls back to the name of the user
    def get_name(self):
        if self.name and self.name.strip():
            return self.name

        first_name = self.user.first_name
        last_name = self.user.last_name
        if not first_name or not first_name.strip():
            return 'Anonymous'
        elif not last_name or not last_name.strip():
            return first_name
        else:
            return first_name + ' ' + last_name.strip()[0] + '.'

    @staticmethod
    def find_by_user(user):
        return Participant.objects.filter(user_id=user.id).order_by('id')


class MoneyRecordType(enum.Enum):
    EXPENSE = 1
    TRANSFER = 2

    @staticmethod
    def from_string(s):
        if s == 'expense':
            return MoneyRecordType.EXPENSE
        elif s == 'transfer':
            return MoneyRecordType.TRANSFER
        else:
            raise Exception("Can't convert to enum value: " + str(s))


class MoneyRecord(models.Model):
    event = models.ForeignKey(Event)
    pub_date = models.DateTimeField('date published')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    type = enum.EnumField(MoneyRecordType)
    participant1 = models.ForeignKey(Participant, related_name='%(class)s_participant1')
    participant2 = models.ForeignKey(Participant, related_name='%(class)s_participant2', blank=True, null=True)

    class Meta:
        db_table = 'mt_money_record'

    def allocations(self):
        return Allocation.objects.filter(money_record_id=self.id)

    def allocation_type(self):
        allocation_type = None
        for allocation in self.allocations():
            assert allocation.type
            if allocation_type is None:
                allocation_type = allocation.type
            else:
                assert allocation_type == allocation.type, 'Mixed allocation types are not supported (corrupt data)'
        return allocation_type

    def equal_allocation_amount(self):
        assert self.allocation_type() == AllocationType.EQUAL, 'Operation supported only for equal allocations'
        equal_amount = self.amount / Decimal(len(self.allocations()))

        # Round the value to two decimal places;
        # The little bit accuracy loss is acceptable for the time being (less than one cent per participant)
        return equal_amount.quantize(Decimal('0.01'), ROUND_DOWN)

    def deep_delete(self):
        with transaction.atomic():
            for allocation in self.allocations():
                allocation.delete()
            self.delete()


class AllocationType(enum.Enum):
    EQUAL = 1
    CUSTOM = 2


class Allocation(models.Model):
    participant = models.ForeignKey(Participant)
    money_record = models.ForeignKey(MoneyRecord)
    type = enum.EnumField(AllocationType)
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=True)

    class Meta:
        db_table = 'mt_allocation'