from django.contrib.auth.models import User
from trakr.models import Event, Participant, MoneyRecord

from trakr.scripts.common import str_date, str_money, str_q


def wipe_all():
    print('Wiping database...')
    MoneyRecord.objects.all().delete()
    Participant.objects.all().delete()
    Event.objects.all().delete()
    User.objects.all().delete()
    print()


def list_users():
    print('User records in database:')
    for user in User.objects.all().order_by('id'):
        print("id: {0}, username: {1}".format(user.id, user.username))
    print()


def list_events():
    print('Event records in database:')
    for event in Event.objects.all().order_by('id'):
        participant_names = []
        for participant in event.participants():
            participant_names.append(participant.get_name())
        print("id: {0}, name: \"{1}\", name slug: {2}, participants: {3}"
              .format(event.id, event.name, event.name_slug, participant_names)
        )
    print()


def list_money_records():
    print('MoneyRecord records in database:')
    participant_name = lambda participant: participant.get_name() if participant else 'NONE'
    for money_record in MoneyRecord.objects.all().order_by('id'):
        print("id: {0}, description: {1}, date: {2}, amount: {3}, participant1: {4}, participant2: {5}"
              .format(money_record.id,
                      str_q(money_record.description),
                      str_date(money_record.pub_date),
                      str_money(money_record.amount),
                      participant_name(money_record.participant1),
                      participant_name(money_record.participant2)
                )
        )
    print()


def list_all():
    list_users()
    list_events()
    list_money_records()

