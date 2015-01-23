from datetime import datetime as dt
from django.utils import timezone as tz

from expenses.models import Event, Person, MoneyRecord, Participant

from expenses.scripts import db


def create_event(name):
    event = Event.objects.create(name=name)
    Event.save(event)
    return event


def create_person(name):
    person = Person.objects.create(name=name)
    Person.save(person)
    return person


def create_participant(event, person):
    participant = Participant.objects.create(event=event, person=person)
    Participant.save(participant)
    return participant


def create_record(event, date_str, description, amount, participant1, participant2=None):
    assert event
    date = date_from_str(date_str)
    assert type(amount) is float
    assert participant1
    if participant2 and not description:
        description = 'Balance transfer from ' + participant1.person.name + ' to ' + participant2.person.name
    else:
        assert description

    money_record = MoneyRecord.objects.create(
        event=event,
        pub_date=date,
        description=description,
        amount=amount,
        participant1=participant1,
        participant2=participant2,
    )
    MoneyRecord.save(money_record)
    return money_record


def date_from_ymd(year, month, day):
    return tz.make_aware(dt(year=year, month=month, day=day), timezone=tz.utc)


def date_from_str(date_str):
    date = dt.strptime(date_str, '%Y/%m/%d')
    return tz.make_aware(date, timezone=tz.utc)


def create_data():

    print('Creating Event records...')
    revy = create_event('Revelstoke Bluebird Jam 2014')

    print('Creating Person records...')
    person_jules = create_person('Jules')
    person_jeremy = create_person('Jeremy')
    person_paul = create_person('Paul')
    person_valdis = create_person('Valdis')

    print('Creating Participant records...')
    revy_jules = create_participant(revy, person_jules)
    revy_jeremy = create_participant(revy, person_jeremy)
    revy_paul = create_participant(revy, person_paul)
    revy_valdis = create_participant(revy, person_valdis)

    print('Creating MoneyRecord records...')
    create_record(revy, '2014/09/28', 'B&B - first installment (50%)', 500.00, revy_jules)
    create_record(revy, '2014/09/28', 'Car rental - first installment', 462.00, revy_jules)
    create_record(revy, '2014/10/08', None, 320.00, revy_paul, revy_jules)     # type: email
    create_record(revy, '2014/10/08', None, 320.00, revy_jeremy, revy_jules)   # type: email
    create_record(revy, '2014/11/28', 'Taxi ride to Pearson Airport', 60.00, revy_jeremy)
    create_record(revy, '2014/11/28', 'Costco - food', 319.00, revy_jules)
    create_record(revy, '2014/11/28', 'Costco - Revelstoke tickets x 30 ($63 per ticket)', 1890.00, revy_jules)
    create_record(revy, '2014/11/28', 'Costco - Revelstoke tickets x -2 (Jer & Valdis paid cash)', -126.00, revy_jules)
    create_record(revy, '2014/11/28', 'Dollarama - Kelowna', 10.00, revy_paul)
    create_record(revy, '2014/11/28', 'IGA - Kelowna', 5.00, revy_paul)
    create_record(revy, '2014/11/30', 'Southside Grocery', 10.00, revy_paul)
    create_record(revy, '2014/11/30', 'Southside Grocery', 11.00, revy_paul)
    create_record(revy, '2014/11/30', 'B&B - second installment (50%)', 500.00, revy_valdis)
    create_record(revy, '2014/11/30', None, 200.00, revy_jeremy, revy_jules)  # type: cash
    create_record(revy, '2014/11/30', None, 600.00, revy_paul, revy_jules)    # type: email
    create_record(revy, '2014/11/30', None, 436.50, revy_valdis, revy_jules)  # type: email
    create_record(revy, '2014/12/01', None, 100.00, revy_jeremy, revy_jules)  # type: cash
    create_record(revy, '2014/12/01', 'Mt. Begbie Brewery', 50.00, revy_paul)
    create_record(revy, '2014/12/02', 'Southside Grocery', 51.50, revy_paul)
    create_record(revy, '2014/12/03', 'Southside Grocery', 18.50, revy_jules)
    create_record(revy, '2014/12/03', 'Taxi to Last Drop', 12.00, revy_jules)
    create_record(revy, '2014/12/04', 'Farmers market', 13.00, revy_jules)
    create_record(revy, '2014/12/06', 'Southside Grocery', 34.00, revy_paul)
    create_record(revy, '2014/12/06', 'Coopers Foods', 7.50, revy_paul)
    create_record(revy, '2014/12/07', 'Southside Grocery', 12.00, revy_paul)
    create_record(revy, '2014/12/07', 'Gas (1 - Revelstoke)', 30.00, revy_jeremy)
    create_record(revy, '2014/12/08', 'Gas (2 - Enderby)', 67.00, revy_jeremy)
    create_record(revy, '2014/12/08', 'Gas (3 - Kelowna)', 8.50, revy_jeremy)
    create_record(revy, '2014/12/08', 'Car rental - second payment', 126.00, revy_jules)
    create_record(revy, '2014/12/08', 'Taxi ride from Pearson Airport', 65.00, revy_jeremy)
    create_record(revy, '2014/12/15', 'End of trip settlement', 183.50, revy_jeremy, revy_jules)
    create_record(revy, '2014/12/15', 'End of trip settlement', 20.50, revy_valdis, revy_jules)
    create_record(revy, '2014/12/15', 'End of trip settlement', 77.00, revy_valdis, revy_paul)

    print()


def run():
    db.wipe_all()
    create_data()
    db.list_all()
    print('Kthxbai.')



