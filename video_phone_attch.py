from calendar_auth import get_calendar_service

def create_event_with_meet():
    service = get_calendar_service()

    event = {
        'summary': 'Team Standup',
        'description': 'Daily standup meeting via Google Meet.',
        'start': {
            'dateTime': '2024-02-20T09:00:00',
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': '2024-02-20T09:30:00',
            'timeZone': 'Europe/London',
        },
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                },
                'requestId': 'meeting-123'  # A unique ID for each request
            }
        },
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    print(f"Event created: {event.get('id')}")
    print(f"Google Meet Link: {event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri')}")

if __name__ == "__main__":
    create_event_with_meet()
