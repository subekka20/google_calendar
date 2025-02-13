from calendar_auth import get_calendar_service

def watch_calendar():
    service = get_calendar_service()

    request = {
        "id": "77t9v2q7hmicc2rrka6o8he6mk",  # Unique ID for the channel
        "type": "web_hook",
        "address": "https://your-webhook-url.com/webhook",  # Your webhook URL
    }

    response = service.events().watch(calendarId='primary', body=request).execute()
    print(f"Watch Channel Created: {response}")

if __name__ == "__main__":
    watch_calendar()
