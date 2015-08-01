from django.contrib.auth.models import User
from django.test import TestCase

from moneytracker.models import Event, Participant, MoneyRecord
from moneytracker.scripts.db_create import create_expense


class EventModelTests(TestCase):

    def setUp(self):
        self.assertTrue(len(Event.objects.all()) == 0, 'Start with and empty database')
        self.assertTrue(len(User.objects.all()) == 0, 'Start with and empty database')
        self.assertTrue(len(Participant.objects.all()) == 0, 'Start with and empty database')


    def test_name_slug_is_derived_from_event_name(self):
        Event.objects.create(name='Oktoberfest 2015', name_slug='this-value-will-be-overwritten').save()

        events_from_db = Event.objects.all()
        self.assertEqual(len(events_from_db), 1, 'Event is now in database')

        event_from_db = events_from_db[0]
        self.assertTrue(event_from_db, 'Event was found in database')
        self.assertEqual(event_from_db.name, 'Oktoberfest 2015', 'Event has expected name')
        self.assertEqual(event_from_db.name_slug, 'oktoberfest-2015', 'Name slug was derived from event name')


    def test_method_find_by_name_slug(self):
        Event.objects.create(name='Sunshine Village').save()
        Event.objects.create(name='Oktoberfest 2015').save()
        Event.objects.create(name='Backpacking Thailand').save()

        events_from_db = Event.objects.all()
        self.assertEqual(len(events_from_db), 3, 'All three events are now in database')

        event_from_db = Event.find_by_name_slug('oktoberfest-2015')
        self.assertTrue(event_from_db, 'Event was found in database')
        self.assertEqual(event_from_db.name, 'Oktoberfest 2015', 'Event has expected name')
        self.assertEqual(event_from_db.name_slug, 'oktoberfest-2015', 'Event has expected name slug')

        event_not_found = Event.find_by_name_slug('oktoberfest-1999')
        self.assertIsNone(event_not_found, 'Event not found for non-existent name slug')


    def test_get_participants(self):
        event1 = Event.objects.create(name='Sunshine Village')
        event1.save()
        event2 = Event.objects.create(name='Oktoberfest 2015')
        event2.save()
        event3 = Event.objects.create(name='Backpacking Thailand')
        event3.save()
        self.assertEqual(len(Event.objects.all()), 3, 'All records saved')

        user1 = User.objects.create(username='john')
        user1.save()
        user2 = User.objects.create(username='michael')
        user2.save()
        user3 = User.objects.create(username='david')
        user3.save()
        self.assertEqual(len(User.objects.all()), 3, 'All records saved')

        par_user1_event1 = Participant.objects.create(user=user1, event=event1, name='John')
        par_user1_event1.save()
        par_user1_event2 = Participant.objects.create(user=user1, event=event2, name='Johnny')
        par_user1_event2.save()

        par_user2_event2 = Participant.objects.create(user=user2, event=event2, name='Mikey')
        par_user2_event2.save()
        par_user2_event3 = Participant.objects.create(user=user2, event=event3, name='Michael')
        par_user2_event3.save()
        self.assertEqual(len(Participant.objects.all()), 4, 'All records saved')


        participants_event1 = event1.participants()
        participants_event2 = event2.participants()
        participants_event3 = event3.participants()

        self.assertEqual(len(participants_event1), 1, 'participant count for event1')
        self.assertEqual(participants_event1[0].name, 'John', 'participant name (event1)')

        self.assertEqual(len(participants_event2), 2, 'participant count for event2')
        self.assertEqual(participants_event2[0].name, 'Johnny', 'participant name (event2)')
        self.assertEqual(participants_event2[1].name, 'Mikey', 'participant name (event2)')

        self.assertEqual(len(participants_event3), 1, 'participant count for event3')
        self.assertEqual(participants_event3[0].name, 'Michael', 'participant name (event3)')


    def test_find_by_user(self):
        event1 = Event.objects.create(name='Sunshine Village')
        event1.save()
        event2 = Event.objects.create(name='Oktoberfest 2015')
        event2.save()
        event3 = Event.objects.create(name='Backpacking Thailand')
        event3.save()

        user1 = User.objects.create(username='john')
        user1.save()
        user2 = User.objects.create(username='michael')
        user2.save()
        user3 = User.objects.create(username='david')
        user3.save()

        par_user1_event1 = Participant.objects.create(user=user1, event=event1, name='John')
        par_user1_event1.save()
        par_user1_event2 = Participant.objects.create(user=user1, event=event2, name='Johnny')
        par_user1_event2.save()

        par_user2_event2 = Participant.objects.create(user=user2, event=event2, name='Mikey')
        par_user2_event2.save()
        par_user2_event3 = Participant.objects.create(user=user2, event=event3, name='Michael')
        par_user2_event3.save()

        self.assertEqual(len(Event.objects.all()), 3, 'All records saved')
        self.assertEqual(len(User.objects.all()), 3, 'All records saved')
        self.assertEqual(len(Participant.objects.all()), 4, 'All records saved')

        events_user1 = Event.find_by_user(user1)
        events_user2 = Event.find_by_user(user2)
        events_user3 = Event.find_by_user(user3)

        self.assertEqual(len(events_user1), 2, 'user1 expected event count')
        self.assertEqual(len(events_user2), 2, 'user2 expected event count')
        self.assertEqual(len(events_user3), 0, 'user3 expected event count (none)')

        self.assertEqual(events_user1[0].name, 'Sunshine Village', 'user1 event 1')
        self.assertEqual(events_user1[1].name, 'Oktoberfest 2015', 'user1 event 2')

        self.assertEqual(events_user2[0].name, 'Oktoberfest 2015', 'user2 event 1')
        self.assertEqual(events_user2[1].name, 'Backpacking Thailand', 'user2 event 2')


    def test_get_money_records(self):
        event1 = Event.objects.create(name='Sunshine Village')
        event1.save()
        event2 = Event.objects.create(name='Oktoberfest 2015')
        event2.save()
        self.assertEqual(len(Event.objects.all()), 2, 'All events saved')

        user1 = User.objects.create(username='john')
        user1.save()
        user2 = User.objects.create(username='michael')
        user2.save()
        self.assertEqual(len(User.objects.all()), 2, 'All users saved')

        par_user1_event1 = Participant.objects.create(user=user1, event=event1, name='John')
        par_user1_event1.save()
        par_user1_event2 = Participant.objects.create(user=user1, event=event2, name='Johnny')
        par_user1_event2.save()
        par_user2_event1 = Participant.objects.create(user=user2, event=event2, name='Mike')
        par_user2_event1.save()
        par_user3_event2 = Participant.objects.create(user=user2, event=event2, name='Mikey')
        par_user3_event2.save()
        self.assertEqual(len(Participant.objects.all()), 4, 'All participants saved')

        # money records for event2
        create_expense(event2, '2014/05/05', 'event2::record1', 1000.00, par_user1_event2)
        # money records for event1
        create_expense(event1, '2014/01/05', 'event1::record1', 10.00, par_user1_event1)
        create_expense(event1, '2014/01/01', 'event1::record2', 15.00, par_user2_event1)
        create_expense(event1, '2014/01/03', 'event1::record3', 9.32, par_user2_event1)
        create_expense(event1, '2014/01/01', 'event1::record4', 5.75, par_user1_event1)

        self.assertEqual(len(MoneyRecord.objects.all()), 5, 'All money records saved')

        event1_records = event1.money_records()
        event2_records = event2.money_records()

        self.assertTrue(len(event1_records) == 4, 'expected record count for event 1')
        self.assertEquals(event1_records[0].description, 'event1::record2', 'ordered by date (asc), then within same date by id (asc)')
        self.assertEquals(event1_records[1].description, 'event1::record4', 'ordered by date (asc), then within same date by id (asc)')
        self.assertEquals(event1_records[2].description, 'event1::record3', 'ordered by date (asc), then within same date by id (asc)')
        self.assertEquals(event1_records[3].description, 'event1::record1', 'ordered by date (asc), then within same date by id (asc)')

        self.assertTrue(len(event2_records) == 1, 'expected record count for event 2')
        self.assertEquals(event2_records[0].description, 'event2::record1', 'ordered by date (asc), then within same date by id (asc)')










