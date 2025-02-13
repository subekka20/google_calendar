from calendar_auth import get_calendar_service
def check_availability():
    service = get_calendar_service()

    request_body = {
        "timeMin": "2025-02-20T09:00:00Z",
        "timeMax": "2025-02-20T10:00:00Z",
        "items": [{"id": "primary"}]  # Check your own calendar
    }

    response = service.freebusy().query(body=request_body).execute()
    busy_slots = response.get("calendars", {}).get("primary", {}).get("busy", [])

    if busy_slots:
        print("Time slot is NOT available.")
    else:
        print("Time slot is available.")

if __name__ == "__main__":
    check_availability()
