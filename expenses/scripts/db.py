from expenses.models import Event, Person, Participant, MoneyRecord

from expenses.scripts.common import str_date, str_money, str_q


def wipe_all():
    print('Wiping database...')
    MoneyRecord.objects.all().delete()
    Participant.objects.all().delete()
    Person.objects.all().delete()
    Event.objects.all().delete()
    print()


def list_persons():
    print('Person records in database:')
    for person in Person.objects.all().order_by('id'):
        print("id: {0}, name: {1}"
              .format(person.id, person.name))
    print()


def list_events():
    print('Event records in database:')
    for event in Event.objects.all().order_by('id'):
        participant_names = []
        for participant in event.participants():
            participant_names.append(participant.person.name)
        print("id: {0}, name: \"{1}\", name slug: {2}, participants: {3}"
              .format(event.id, event.name, event.name_slug, participant_names)
        )
    print()


def list_money_records():
    print('MoneyRecord records in database:')
    participant_name = lambda participant: participant.person.name if participant else 'NONE'
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
    list_persons()
    list_events()
    list_money_records()

