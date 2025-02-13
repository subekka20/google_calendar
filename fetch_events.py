from calendar_auth import get_calendar_service

def list_events():
    service = get_calendar_service()
    now = '2024-02-11T00:00:00Z'  # Change the date as needed
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_id = event.get('id')  # Get event ID
        print(f"{start} - {event['summary']} (ID: {event_id})")

if __name__ == "__main__":
    list_events()
