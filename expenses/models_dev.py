from expenses.models import Event, Person, Participant, Expense, Contribution

def event_participants_str(event):
    s_person_names = []
    for person in event.participants():
        s_person_names.append(person.name)
    return ', '.join(s_person_names)

def expense_contributions_str(expense):
    s_contributions = []
    for contribution in expense.contributions():
        s_contributions.append(contribution.participant.person.name + ': ' + money_amount_str(contribution.amount))
    return '{' + ', '.join(s_contributions) + '}'

def money_amount_str(amount):
    return "${0:.2f}".format(amount)