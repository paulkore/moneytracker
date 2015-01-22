from django.db import models
from django.http import Http404
from django.template.defaultfilters import slugify


class Event(models.Model):
    name = models.CharField(max_length=100)
    name_slug = models.SlugField(max_length=100)

    class Meta:
        db_table = 'mt_event'

    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)

    def participants(self):
        return Participant.objects.filter(event_id=self.id).order_by('id')

    def participant_persons(self):
        person_ids = []
        for participant in self.participant_objects():
            person_ids.append(participant.person_id)
        return Person.objects.filter(id__in=person_ids).order_by('id')

    def money_records(self):
        return MoneyRecord.objects.filter(event_id=self.id).order_by('id')

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
        db_table = 'mt_person'


class Participant(models.Model):
    person = models.ForeignKey(Person)
    event = models.ForeignKey(Event)

    class Meta:
        db_table = 'mt_participant'


class MoneyRecord(models.Model):
    event = models.ForeignKey(Event)
    pub_date = models.DateTimeField('date published')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    participant1 = models.ForeignKey(Participant, related_name='%(class)s_participant1')
    participant2 = models.ForeignKey(Participant, related_name='%(class)s_participant2', blank=True, null=True)

    class Meta:
        db_table = 'mt_money_record'
