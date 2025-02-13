from calendar_auth import get_calendar_service

CALENDAR_ID = 'primary'

def list_events(event_type=None):
    """Lists events based on type (default, birthday, fromGmail) by manually filtering."""
    service = get_calendar_service()
    
    query_params = {
        'calendarId': CALENDAR_ID,
        'singleEvents': True,
        'timeMin': '2025-07-29T00:00:00Z',
        'timeMax': '2025-07-30T00:00:00Z',
        'maxResults': 50,  # Increase if needed
    }

    try:
        events_result = service.events().list(**query_params).execute()
        events = events_result.get('items', [])

        if not events:
            print(f"No {event_type or 'all'} events found.")
            return

        # Manually filter events by type
        for event in events:
            if event_type and event.get('eventType', 'default') != event_type:
                continue  # Skip non-matching events

            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']} (ID: {event['id']}, Type: {event.get('eventType', 'default')})")
    except Exception as e:
        print(f"Error: {e}")


### READ EVENT ###
def read_event(event_id):
    """Reads an event by its ID."""
    service = get_calendar_service()
    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        print(event)
    except Exception as e:
        print(f"Error reading event: {e}")


### CREATE A DEFAULT EVENT ###
def create_default_event():
    """Creates a standard calendar event."""
    event = {
        'summary': 'Sample Event',
        'description': 'Created from Python script.',
        'start': {'dateTime': '2025-07-30T10:30:00+01:00', 'timeZone': 'Europe/London'},
        'end': {'dateTime': '2025-07-30T12:30:00+01:00', 'timeZone': 'Europe/London'},
        'eventType': 'default',
    }
    create_event(event)


### CREATE A BIRTHDAY EVENT ###
def create_birthday_event():
    """Creates a recurring birthday event."""
    event = {
        'summary': "My Friend's Birthday",
        'start': {'date': '2025-01-29'},  # All-day event
        'end': {'date': '2025-01-30'},
        'eventType': 'birthday',
        'recurrence': ["RRULE:FREQ=YEARLY"],  # Recurring every year
        'transparency': "transparent",
        'visibility': "private",
    }
    create_event(event)


### CREATE AN EVENT FUNCTION ###
def create_event(event):
    """Creates a new Google Calendar event."""
    service = get_calendar_service()
    try:
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f"Event created: {created_event.get('htmlLink')}")
        print(f"Event ID: {created_event.get('id')}")
    except Exception as e:
        print(f"Error creating event: {e}")


### MAIN EXECUTION ###
if __name__ == "__main__":
    print("\nListing Default Events:")
    list_events('default')

    print("\nListing Birthday Events:")
    list_events('birthday')

    print("\nListing Events from Gmail:")
    list_events('fromGmail')

    print("\nCreating a Default Event:")
    create_default_event()

    print("\nCreating a Birthday Event:")
    create_birthday_event()
