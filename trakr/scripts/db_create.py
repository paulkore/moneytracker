from datetime import datetime as dt
from django.utils import timezone as tz
from django.contrib.auth.models import User

from moneytracker.models import Event, Participant, MoneyRecord, MoneyRecordType, Allocation, AllocationType
from moneytracker.scripts import db


def create_event(name):
    event = Event.objects.create(name=name)
    Event.save(event)
    return event


def create_user(username, email, password, first_name, last_name):
    user = User.objects.create_user(username, email, password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    return user


def create_participant(event, user):
    participant = Participant.objects.create(event=event, user=user, name=user.first_name)
    Participant.save(participant)
    return participant


def create_expense(event, date_str, description, amount, participant):
    expense = MoneyRecord.objects.create(
        event=event,
        pub_date=date_from_str(date_str),
        description=description,
        amount=amount,
        type=MoneyRecordType.EXPENSE,
        participant1=participant,
        participant2=None,
    )
    MoneyRecord.save(expense)

    for participant in event.participants():
        new_allocation = Allocation.objects.create(
            money_record=expense,
            participant_id=participant.id,
            type=AllocationType.EQUAL,
            amount=None,
        )
        new_allocation.save()

    return expense


def create_transfer(event, date_str, amount, participant_from, participant_to):
    transfer = MoneyRecord.objects.create(
        event=event,
        pub_date=date_from_str(date_str),
        description='Transfer of funds',
        amount=amount,
        type=MoneyRecordType.TRANSFER,
        participant1=participant_from,
        participant2=participant_to,
    )
    MoneyRecord.save(transfer)
    return transfer


def date_from_ymd(year, month, day):
    return tz.make_aware(dt(year=year, month=month, day=day), timezone=tz.utc)


def date_from_str(date_str):
    date = dt.strptime(date_str, '%Y/%m/%d')
    return tz.make_aware(date, timezone=tz.utc)


def create_data():

    print('Creating users...')
    user_jules = create_user('jules', 'info@nowhere.com', 'foo', 'Jules', 'A.')
    user_jeremy = create_user('jeremy', 'info@nowhere.com', 'foo', 'Jeremy', 'W.')
    user_paul = create_user('paul', 'info@nowhere.com', 'foo', 'Paul', 'K.')
    user_valdis = create_user('valdis', 'info@nowhere.com', 'foo', 'Valdis', 'U.')

    print('Creating events...')
    revy = create_event('Revelstoke Bluebird Jam 2014')

    print('Creating participants...')
    revy_jules = create_participant(revy, user_jules)
    revy_jeremy = create_participant(revy, user_jeremy)
    revy_paul = create_participant(revy, user_paul)
    revy_valdis = create_participant(revy, user_valdis)

    print('Creating money records...')
    create_expense(revy, '2014/09/28', 'B&B - first payment (50%)', 500.00, revy_jules)
    create_expense(revy, '2014/09/28', 'Car rental - first payment', 462.00, revy_jules)
    create_transfer(revy, '2014/10/08', 320.00, revy_paul, revy_jules)
    create_transfer(revy, '2014/10/08', 320.00, revy_jeremy, revy_jules)
    create_expense(revy, '2014/11/28', 'Taxi ride to Pearson Airport', 60.00, revy_jeremy)
    create_expense(revy, '2014/11/28', 'Costco - food', 319.00, revy_jules)
    create_expense(revy, '2014/11/28', 'Costco - Revelstoke tickets x 30 ($63 per ticket)', 1890.00, revy_jules)
    create_expense(revy, '2014/11/28', 'Credit for 2 Revelstoke tickets (Jeremy and Valdis paid cash)', -126.00, revy_jules)
    create_expense(revy, '2014/11/28', 'Dollarama - Kelowna', 10.00, revy_paul)
    create_expense(revy, '2014/11/28', 'IGA - Kelowna', 5.00, revy_paul)
    create_expense(revy, '2014/11/30', 'Southside Grocery', 10.00, revy_paul)
    create_expense(revy, '2014/11/30', 'Southside Grocery', 11.00, revy_paul)
    create_expense(revy, '2014/11/30', 'B&B - second payment (50%)', 500.00, revy_valdis)
    create_transfer(revy, '2014/11/30', 200.00, revy_jeremy, revy_jules)
    create_transfer(revy, '2014/11/30', 600.00, revy_paul, revy_jules)
    create_transfer(revy, '2014/11/30', 436.50, revy_valdis, revy_jules)
    create_transfer(revy, '2014/12/01', 100.00, revy_jeremy, revy_jules)
    create_expense(revy, '2014/12/01', 'Mt. Begbie Brewery', 50.00, revy_paul)
    create_expense(revy, '2014/12/02', 'Southside Grocery', 51.50, revy_paul)
    create_expense(revy, '2014/12/03', 'Southside Grocery', 18.50, revy_jules)
    create_expense(revy, '2014/12/03', 'Taxi to Last Drop', 12.00, revy_jules)
    create_expense(revy, '2014/12/04', 'Farmers market', 13.00, revy_jules)
    create_expense(revy, '2014/12/06', 'Southside Grocery', 34.00, revy_paul)
    create_expense(revy, '2014/12/06', 'Coopers Foods', 7.50, revy_paul)
    create_expense(revy, '2014/12/07', 'Southside Grocery', 12.00, revy_paul)
    create_expense(revy, '2014/12/07', 'Gas (1 - Revelstoke)', 30.00, revy_jeremy)
    create_expense(revy, '2014/12/08', 'Gas (2 - Enderby)', 67.00, revy_jeremy)
    create_expense(revy, '2014/12/08', 'Gas (3 - Kelowna)', 8.50, revy_jeremy)
    create_expense(revy, '2014/12/08', 'Car rental - second payment', 126.00, revy_jules)
    create_expense(revy, '2014/12/08', 'Taxi ride from Pearson Airport', 65.00, revy_jeremy)
    create_transfer(revy, '2014/12/15', 183.50, revy_jeremy, revy_jules)
    create_transfer(revy, '2014/12/15', 20.50, revy_valdis, revy_jules)
    create_transfer(revy, '2014/12/15', 77.00, revy_valdis, revy_paul)

    print()


def run():
    db.wipe_all()
    create_data()
    db.list_all()
    print('Kthxbai.')



