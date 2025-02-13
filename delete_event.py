from calendar_auth import get_calendar_service

def delete_event(event_id):
    service = get_calendar_service()
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    print(f"Event {event_id} deleted successfully.")

if __name__ == "__main__":
    event_id = "77t9v2q7hmicc2rrka6o8he6mk"
    delete_event(event_id)
