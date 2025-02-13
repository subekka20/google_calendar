from calendar_auth import get_calendar_service

def update_event(event_id):
    service = get_calendar_service()

    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    
    # Change event details
    event['summary'] = "Updated Meeting with Client"
    event['description'] = "Updated discussion on project."
    event['start']['dateTime'] = '2024-02-15T11:00:00'
    event['end']['dateTime'] = '2024-02-15T12:00:00'

    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    print(f"Event updated: {updated_event.get('htmlLink')}")

if __name__ == "__main__":
    event_id = "211e3okhu245a31547khkner4s"
    update_event(event_id)
