import time
from calendar_auth import get_calendar_service
from googleapiclient.http import BatchHttpRequest

CALENDAR_ID = 'primary'


# ---------------------- LIST EVENTS ---------------------- #
def list_events(event_type=None):
    """Lists events based on type (default, birthday, fromGmail) by manually filtering."""
    service = get_calendar_service()

    time_min = input("Enter start date (YYYY-MM-DDTHH:MM:SSZ) or leave blank for default: ") or "2025-01-02T00:00:00Z"
    time_max = input("Enter end date (YYYY-MM-DDTHH:MM:SSZ) or leave blank for default: ") or "2025-02-28T00:00:00Z"
    query_params = {
        'calendarId': CALENDAR_ID,
        'timeMin': time_min,
        'timeMax': time_max,
        'maxResults': 100,  
    }
    try:
        events_result = service.events().list(**query_params).execute()
        events = events_result.get('items', [])

        if not events:
            print(f"No {event_type or 'all'} events found.")
            return

        for event in events:
            event_type_actual = event.get('eventType', 'default')  # Default if missing

            if 'recurringEventId' in event:
                event_type_actual = 'recurring'
            if event_type and event_type_actual != event_type:
                continue  # Skip non-matching events

            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']} (ID: {event['id']}, Type: {event_type_actual})")
    except Exception as e:
        print(f"Error: {e}")

# ---------------------- READ EVENT ---------------------- #
def read_event():
    """Reads an event by its ID."""
    service = get_calendar_service()
    event_id = input("Enter Event ID to read: ")

    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        print("\n--- Event Details ---")
        print(f"Title: {event.get('summary', 'No Title')}")
        print(f"Start Time: {event['start'].get('dateTime', event['start'].get('date'))}")
        print(f"End Time: {event['end'].get('dateTime', event['end'].get('date'))}")
        print(f"Location: {event.get('location', 'No Location')}")
        print(f"Event Type: {event.get('eventType', 'default')}")
        print(f"Description: {event.get('description', 'No Description')}")
        print(f"Google Meet Link: {event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', 'None')}")
        print("---------------------")

    except Exception as e:
        print(f"Error reading event: {e}")

# ---------------------- CREATE EVENTS ---------------------- #
def create_default_event():
    """Creates a standard calendar event."""
    service = get_calendar_service()

    summary = input("Enter event title: ")
    description = input("Enter event description: ")
    start_time = input("Enter start date and time (YYYY-MM-DDTHH:MM:SSZ): ")
    end_time = input("Enter end date and time (YYYY-MM-DDTHH:MM:SSZ): ")
    timezone = "UTC"

    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': timezone},
        'end': {'dateTime': end_time, 'timeZone': timezone},
        'eventType': 'default',
    }

    create_event(event)


def create_birthday_event():
    """Creates a recurring birthday event."""
    service = get_calendar_service()

    summary = input("Enter birthday event title: ")
    date = input("Enter birthday date (YYYY-MM-DD): ")

    event = {
        'summary': summary,
        'start': {'date': date},
        'end': {'date': date},
        'eventType': 'birthday',
        'recurrence': ["RRULE:FREQ=YEARLY"],
        'transparency': "transparent",
        'visibility': "private",
    }

    create_event(event)


def create_event(event):
    """Creates a new Google Calendar event."""
    service = get_calendar_service()
    try:
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f"Event created successfully!")
        print(f"Event ID: {created_event.get('id')}")
    except Exception as e:
        print(f"Error creating event: {e}")


# ---------------------- UPDATE EVENT ---------------------- #
def update_event():
    service = get_calendar_service()
    event_id = input("Enter Event ID to update: ")

    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        updated_title = input(f"Enter new title (leave blank to keep '{event.get('summary', 'No Title')}'): ")
        update_start_time = input(f"Enter new start date and time (YYYY-MM-DDTHH:MM:SSZ, leave blank to keep '{event.get('start', {}).get('dateTime', 'No Start Time')}'): ")
        update_end_time = input(f"Enter new end date and time (YYYY-MM-DDTHH:MM:SSZ, leave blank to keep '{event.get('end', {}).get('dateTime', 'No End Time')}'): ")

        if updated_title:
            event['summary'] = updated_title
        if update_start_time:
            event.setdefault('start', {})
            event['start']['dateTime'] = update_start_time
            event['start']['timeZone'] = event.get('start', {}).get('timeZone', 'UTC')
        if update_end_time:
            event.setdefault('end', {})
            event['end']['dateTime'] = update_end_time
            event['end']['timeZone'] = event.get('end', {}).get('timeZone', 'UTC')

        updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
        print(f"Event Updated successfully!")
        print(f"Event ID: {updated_event.get('id')}")

    except Exception as e:
        print(f"Error updating event: {e}")


# ---------------------- DELETE EVENT ---------------------- #
def delete_event():
    """Deletes an event."""
    service = get_calendar_service()
    event_id = input("Enter Event ID to delete: ")

    try:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        print("Event deleted successfully.")
    except Exception as e:
        print(f"Error deleting event: {e}")

# ---------------------- CHECK AVAILABILITY ---------------------- #
def check_availability():
    """Checks if a time slot is available."""
    service = get_calendar_service()

    start_time = input("Enter start date and time (YYYY-MM-DDTHH:MM:SSZ): ")
    end_time = input("Enter end date and time (YYYY-MM-DDTHH:MM:SSZ): ")

    request_body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "items": [{"id": "primary"}]
    }

    response = service.freebusy().query(body=request_body).execute()
    busy_slots = response.get("calendars", {}).get("primary", {}).get("busy", [])

    print("Time slot is available." if not busy_slots else "Time slot is NOT available.")

# ---------------------- CREATE EVENT WITH ATTACHMENT ---------------------- #
def create_event_with_attachment():
    """Creates an event with a Google Drive attachment."""
    service = get_calendar_service()

    summary = input("Enter event title: ")
    file_url = input("Enter Google Drive file URL: ")

    event = {
        'summary': summary,
        'start': {'dateTime': '2025-02-28T10:28:00+01:00', 'timeZone': 'Europe/London'},
        'end': {'dateTime': '2025-02-28T12:30:00+01:00', 'timeZone': 'Europe/London'},
        'attachments': [{'fileUrl': file_url, 'title': 'Attachment'}],
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")

# ---------------------- CREATE EVENT WITH GOOGLE MEET ---------------------- #
def create_event_with_meet():
    """Creates an event with a Google Meet link."""
    service = get_calendar_service()

    summary = input("Enter event title: ")
    start_time = input("Enter start date and time (YYYY-MM-DDTHH:MM:SS+HH:MM): ")
    end_time = input("Enter end date and time (YYYY-MM-DDTHH:MM:SS+HH:MM): ")
    timezone = "UTC"

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': timezone},
        'end': {'dateTime': end_time, 'timeZone': timezone},
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                'requestId': f'meeting-{int(time.time())}' 
            }
        },
    }

    try:
        event = service.events().insert(
            calendarId=CALENDAR_ID, body=event, conferenceDataVersion=1
        ).execute()
        print(f"Event created: {event.get('htmlLink')}")
        print(f"Google Meet Link: {event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri')}")
    except Exception as e:
        print(f"Error creating event: {e}")

# ---------------------- WATCH CALENDAR ---------------------- #
def watch_calendar():
    """Sets up push notifications for event changes."""
    service = get_calendar_service()

    webhook_url = input("Enter webhook URL: ")
    webhook_id = input("Enter webhook id: ")

    request = {
        "id": webhook_id,
        "type": "web_hook",
        "address": webhook_url,
    }

    response = service.events().watch(calendarId=CALENDAR_ID, body=request).execute()
    print(f"Watch Channel Created: {response}")

# ---------------------- ADD USER ACCESS ---------------------- #
def grant_access():
    """Grants a user access to the calendar."""
    service = get_calendar_service()
    user_email = input("Enter the email of the user to grant access: ")
    role = input("Enter role (reader/writer/owner): ") or "reader"

    rule = {
        "role": role,
        "scope": {"type": "user", "value": user_email},
    }

    try:
        service.acl().insert(calendarId=CALENDAR_ID, body=rule).execute()
        print(f"Access granted to {user_email} as {role}.")
    except Exception as e:
        print(f"Error granting access: {e}")

# ---------------------- REMOVE USER ACCESS ---------------------- #
def remove_access():
    """Revokes a user's access to the calendar."""
    service = get_calendar_service()
    user_email = input("Enter the email of the user to remove access: ")

    try:
        # Fetch existing ACL rules
        acl_rules = service.acl().list(calendarId=CALENDAR_ID).execute()
        for rule in acl_rules.get("items", []):
            if rule["scope"].get("type") == "user" and rule["scope"].get("value") == user_email:
                rule_id = rule["id"]
                service.acl().delete(calendarId=CALENDAR_ID, ruleId=rule_id).execute()
                print(f"Access revoked for {user_email}.")
                return
        print("User does not have explicit access to this calendar.")
    except Exception as e:
        print(f"Error removing access: {e}")

# ---------------------- INVITE USERS TO AN EVENT ---------------------- #
def invite_users_to_event():
    """Invites users to an existing event by adding attendees."""
    service = get_calendar_service()
    event_id = input("Enter Event ID to invite users: ")
    attendees_emails = input("Enter attendee emails (comma-separated): ").split(',')

    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        if event.get("eventType") == "birthday":
            print("Error: Cannot invite attendees to a birthday event.")
            return

        existing_attendees = event.get("attendees", [])

        for email in attendees_emails:
            existing_attendees.append({"email": email.strip()})

        event["attendees"] = existing_attendees

        updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()

        print(f"Users invited successfully to event: {updated_event.get('htmlLink')}")
    except Exception as e:
        print(f"Error inviting users: {e}")

# ---------------------- ADD REMINDERS & NOTIFICATIONS ---------------------- #
def add_reminders_to_event():
    """Adds reminders and notifications to an event."""
    service = get_calendar_service()
    event_id = input("Enter Event ID to add reminders: ")
    try:
        email_reminder_minutes = int(input("Enter minutes before event for email reminder: ") or 1440)
        popup_reminder_minutes = int(input("Enter minutes before event for popup reminder: ") or 30)
    except ValueError:
        print("Invalid input. Please enter a valid number of minutes.")
        return

    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        event["reminders"] = {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": email_reminder_minutes},
                {"method": "popup", "minutes": popup_reminder_minutes},
            ],
        }
        updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
        print(f"Reminders added successfully to event: {updated_event.get('htmlLink')}")
    except Exception as e:
        print(f"Error adding reminders: {e}")

# ---------------------- MANAGE DOMAIN RESOURCES, ROOMS & CALENDARS ---------------------- #
def list_domain_resources():
    """Lists available domain resources (e.g., rooms, shared calendars)."""
    service = get_calendar_service()
    try:
        resources = service.calendarList().list().execute()
        for resource in resources.get("items", []):
            print(f"Resource Name: {resource.get('summary')}, ID: {resource.get('id')}")
    except Exception as e:
        print(f"Error retrieving domain resources: {e}")

# ---------------------- ADD EXTENDED PROPERTIES ---------------------- #
def add_extended_properties():
    """Adds extended properties to an event."""
    service = get_calendar_service()
    event_id = input("Enter Event ID to add extended properties: ")
    key = input("Enter extended property key: ")
    value = input("Enter extended property value: ")

    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        extended_properties = event.get("extendedProperties", {}).get("private", {})
        extended_properties[key] = value
        event["extendedProperties"] = {"private": extended_properties}

        updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
        print(f"Extended property added successfully to event: {updated_event.get('htmlLink')}")
    except Exception as e:
        print(f"Error adding extended properties: {e}")

# ---------------------- SEND BATCH REQUESTS ---------------------- #
def send_batch_requests():
    """Sends multiple API requests in a batch."""
    service = get_calendar_service()
    batch = service.new_batch_http_request()

    def callback(request_id, response, exception):
        if exception:
            print(f"Error in request {request_id}: {exception}")
        else:
            print(f"Request {request_id} executed successfully: {response}")

    request_1 = service.events().list(calendarId=CALENDAR_ID)
    request_2 = service.events().list(calendarId=CALENDAR_ID, maxResults=5)

    batch.add(request_1, callback=callback)
    batch.add(request_2, callback=callback)
    batch.execute()

    print("Batch request executed.")


# ---------------------- MENU SYSTEM ---------------------- #
def main():
    options = {
        "1": ("List Events", list_events),
        "2": ("Read Event", read_event),
        "3": ("Create Event", create_default_event),
        "4": ("Create Birthday Event", create_birthday_event),
        "5": ("Update Event", update_event),
        "6": ("Delete Event", delete_event),
        "7": ("Check Availability", check_availability),
        "8": ("Create Event with Attachment", create_event_with_attachment),
        "9": ("Create Event with Google Meet", create_event_with_meet),
        # "10": ("Watch Calendar for Changes", watch_calendar),
        "10": ("Grant Calendar Access", grant_access),
        "11": ("Remove Calendar Access", remove_access),
        "12": ("Invite Users to an Event", invite_users_to_event),
        "13": ("Add Reminders to an Event", add_reminders_to_event),
        "14": ("List Domain Resources, Rooms & Calendars", list_domain_resources),
        "15": ("Add Extended Properties to Event", add_extended_properties),
        "16": ("Send Batch Requests", send_batch_requests),
        "17": ("Exit", exit)
    }

    while True:
        print("\nSelect an option:")
        for key, (desc, _) in options.items():
            print(f"{key}. {desc}")

        choice = input("Enter the number of the action: ")

        if choice in options:
            options[choice][1]()  # Execute selected function
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
