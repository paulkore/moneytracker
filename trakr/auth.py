from moneytracker.models import Event


def has_event_access(user, event):
    assert user.is_authenticated(), 'Function assumes that user is already authenticated'
    assert type(event) is Event

    participants = event.participants()
    for participant in participants:
        if participant.user_id == user.id:
            return True
    return False






