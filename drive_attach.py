from calendar_auth import get_calendar_service

def create_event_with_attachment():
    service = get_calendar_service()

    event = {
        'summary': 'Project Meeting',
        'location': 'London, UK',
        'description': 'Discuss project requirements with attached document.',
        'start': {
            'dateTime': '2024-02-20T10:00:00',
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': '2024-02-20T11:00:00',
            'timeZone': 'Europe/London',
        },
        'attachments': [
            {
                'fileUrl': 'https://docs.google.com/spreadsheets/d/1mnbvv55CbsVrjIlCPUzfQPxtuAETE1kkOQ7ohby0YTc/edit?usp=share_link',
                'title': 'Project Plan.pdf'
            }
        ],
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")
    print(f"Event ID: {event.get('id')}")

if __name__ == "__main__":
    create_event_with_attachment()
