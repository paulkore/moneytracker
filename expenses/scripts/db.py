from expenses.models import Event, Person, Participant, Expense, Contribution

from expenses.scripts import common
import expenses.models_dev as md

def wipe_all():
    print('Wiping database...')
    Contribution.objects.all().delete()
    Expense.objects.all().delete()
    Participant.objects.all().delete()
    Person.objects.all().delete()
    Event.objects.all().delete()
    print()

def list_persons():
    print('Person records in database:')
    for person in Person.objects.all():
        print("id: {0}, name: {1}"
              .format(person.id, person.name))
    print()

def list_events():
    print('Event records in database:')
    for event in Event.objects.all():
        print("id: {0}, name: \"{1}\", name slug: {2}, participants: {3}"
              .format(event.id, event.name, event.name_slug, md.event_participants_str(event)))
    print()

def list_expenses():
    print('Expense records in database:')
    for expense in Expense.objects.all():
        print("id: {0}, description: \"{1}\", date: {2}, contributions: {3}"
              .format(expense.id, expense.description, common.str_date(expense.pub_date), md.expense_contributions_str(expense)))
    print()

def list_all():
    list_persons()
    list_events()
    list_expenses()