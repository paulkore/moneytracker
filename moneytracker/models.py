from django.contrib.auth.models import User
from django.db import models
from django.http import Http404
from django.template.defaultfilters import slugify


class Event(models.Model):
    name = models.CharField(max_length=100)
    name_slug = models.SlugField(max_length=100)

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
        return MoneyRecord.objects.filter(event_id=self.id).order_by('id')

    @staticmethod
    def find_by_name_slug(name_slug):
        assert type(name_slug) is str
        results = Event.objects.filter(name_slug=name_slug)
        if len(results) == 0:
            raise Http404
        elif len(results) == 1:
            return results[0]
        else:
            raise Exception('Unexpected: more than one event found by name slug: ' + name_slug)

    @staticmethod
    def find_by_user(user):
        event_ids = set()
        participants = Participant.objects.filter(user_id=user.id)
        for participant in participants:
            event_ids.add(participant.event_id)
        events = Event.objects.filter(id__in=event_ids).order_by('id')
        return events


class Participant(models.Model):
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=15, blank=False, null=True)

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
        if not first_name and not first_name.strip():
            return 'Anonymous'
        elif not last_name and not last_name.strip():
            return first_name
        else:
            return first_name + ' ' + last_name.strip()[0] + '.'


class MoneyRecord(models.Model):
    event = models.ForeignKey(Event)
    pub_date = models.DateTimeField('date published')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    participant1 = models.ForeignKey(Participant, related_name='%(class)s_participant1')
    participant2 = models.ForeignKey(Participant, related_name='%(class)s_participant2', blank=True, null=True)

    class Meta:
        db_table = 'mt_money_record'
