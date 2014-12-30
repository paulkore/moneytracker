from django.db import models
from django.http import Http404
from django.template.defaultfilters import slugify
from django.db import transaction

from decimal import Decimal

class Event(models.Model):
    name = models.CharField(max_length=100)
    name_slug = models.SlugField(max_length=100)
    class Meta:
        db_table = 'exp_event'

    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)

    def participant_objects(self):
        return Participant.objects.filter(event_id=self.id)

    def participants(self):
        person_ids = []
        for participant in self.participant_objects():
            person_ids.append(participant.person_id)
        return Person.objects.filter(id__in=person_ids)

    def expenses(self):
        return Expense.objects.filter(event_id=self.id)

    def find_by_name_slug(name_slug):
        assert type(name_slug) is str
        results = Event.objects.filter(name_slug=name_slug)
        if len(results) == 0:
            raise Http404
        elif len(results) == 1:
            return results[0]
        else:
            raise Exception('Unexpected: more than one event found by name slug: ' + name_slug)


class Person(models.Model):
    name = models.CharField(max_length=50)
    class Meta:
        db_table = 'exp_person'


class Participant(models.Model):
    person = models.ForeignKey(Person)
    event = models.ForeignKey(Event)
    class Meta:
        db_table = 'exp_participant'

class Expense(models.Model):
    event = models.ForeignKey(Event)
    pub_date = models.DateTimeField('date published')
    description = models.CharField(max_length=200)
    class Meta:
        db_table = 'exp_expense'

    def contributions(self):
        return Contribution.objects.filter(expense_id=self.id)

    def contributions_dict(self):
        d_contributions = {}
        for contribution in self.contributions():
            d_contributions[contribution.participant.person] = contribution.amount
        return d_contributions

    def total_amount(self):
        total = Decimal(0)
        for contribution in self.contributions():
            total += contribution.amount
        return total

    def deep_delete(self):
        with transaction.atomic():
            for contribution in self.contributions():
                contribution.delete()
            self.delete()


class Contribution(models.Model):
    participant = models.ForeignKey(Participant)
    expense = models.ForeignKey(Expense)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    class Meta:
        db_table = 'exp_contribution'




