from calendar_auth import get_calendar_service  # Ensure this is correct

def create_event():
    service = get_calendar_service()

    event = {
        'summary': 'Meeting with Client',
        'location': 'London, UK',
        'description': 'Discuss project requirements.',
        'start': {
            'dateTime': '2024-02-15T10:00:00',
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': '2024-02-15T11:00:00',
            'timeZone': 'Europe/London',
        },
        'attendees': [
            {'email': 'client@example.com'}
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
        'visibility': 'public',
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")
    print(f"Event ID: {event.get('id')}")

if __name__ == "__main__":
    create_event()
