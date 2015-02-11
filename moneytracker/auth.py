from moneytracker.models import Event


def has_event_access(user, event_name_slug):
    if not user.is_authenticated():
            return False

    event = Event.find_by_name_slug(event_name_slug)
    participants = event.participants()
    for participant in participants:
        if participant.user_id == user.id:
            return True

    return False



