from event import EventLog, Event

e1 = Event.create_event( attributes={'name': 'event1', 'value': 1})
e2 = Event.create_event( attributes={'name': 'event2', 'value': 2})

log = EventLog()
log.add_event(e1)
log.add_event(e2)

log.export_json('events.json')