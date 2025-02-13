import time
from calendar_auth import get_calendar_service
from googleapiclient.http import BatchHttpRequest

CALENDAR_ID = 'primary'


from datetime import datetime, timedelta
import pytz

def list_events():
    """Lists events occurring between a given start and end date."""
    service = get_calendar_service()
    time_min = input("Enter start date (YYYY-MM-DD): ")
    time_max = input("Enter end date (YYYY-MM-DD): ")
    try:
        time_min = datetime.strptime(time_min, "%Y-%m-%d").isoformat() + "Z" 
        time_max = (datetime.strptime(time_max, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)).isoformat() + "Z"

        query_params = {
            'calendarId': CALENDAR_ID,
            'timeMin': time_min,
            'timeMax': time_max,
            'maxResults': 100,
            'singleEvents': True, 
            'orderBy': 'startTime', 
        }
        events_result = service.events().list(**query_params).execute()
        events = events_result.get('items', [])
        if not events:
            print(f"No events found between {time_min} and {time_max}.")
            return
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title') 
            event_id = event.get('id', 'Unknown ID')
            print(f"{start} - {summary} (ID: {event_id})")
    except ValueError:
        print("Invalid date format. Please enter the date in 'YYYY-MM-DD' format.")
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
    """Creates a standard calendar event with user-input start and end time."""
    summary = input("Enter event title: ")
    description = input("Enter event description: ")
    timezone = input("Enter your time zone (e.g., Asia/Kolkata, Europe/London): ").strip()

    try:
        start_input = input("Enter start date and time (YYYY-MM-DD HH:MM AM/PM): ")
        end_input = input("Enter end date and time (YYYY-MM-DD HH:MM AM/PM): ")
        user_timezone = pytz.timezone(timezone)
        start_time = user_timezone.localize(datetime.strptime(start_input, "%Y-%m-%d %I:%M %p")).isoformat()
        end_time = user_timezone.localize(datetime.strptime(end_input, "%Y-%m-%d %I:%M %p")).isoformat()

        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': timezone},  # Store in local timezone
            'end': {'dateTime': end_time, 'timeZone': timezone},
            'eventType': 'default',
        }

        create_event(event)
    except ValueError:
        print("❌ Invalid date format. Please enter in 'YYYY-MM-DD HH:MM AM/PM' format.")
    except pytz.UnknownTimeZoneError:
        print("❌ Invalid time zone. Please enter a valid time zone like 'Asia/Kolkata'.")

def create_birthday_event():
    """Creates a recurring birthday event (date remains user-input)."""
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
        print(f"✅ Event created successfully!")
        print(f"📅 Event ID: {created_event.get('id')}")
        print(f"📍 Event Link: {created_event.get('htmlLink')}")
    except Exception as e:
        print(f"❌ Error creating event: {e}")


# ---------------------- UPDATE EVENT ---------------------- #
def update_event():
    service = get_calendar_service()
    event_id = input("Enter Event ID to update: ")

    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        updated_title = input(f"Enter new title (leave blank to keep '{event.get('summary', 'No Title')}'): ")
        update_start_time = input(f"Enter new start date and time (YYYY-MM-DD HH:MM AM/PM, leave blank to keep '{event.get('start', {}).get('dateTime', 'No Start Time')}'): ")
        update_end_time = input(f"Enter new end date and time (YYYY-MM-DD HH:MM AM/PM, leave blank to keep '{event.get('end', {}).get('dateTime', 'No End Time')}'): ")

        if updated_title:
            event['summary'] = updated_title
        if update_start_time:
            event.setdefault('start', {})
            event['start']['dateTime'] = update_start_time
            event['start']['timeZone'] = event.get('start', {})
        if update_end_time:
            event.setdefault('end', {})
            event['end']['dateTime'] = update_end_time
            event['end']['timeZone'] = event.get('end', {})

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
    """Checks if a time slot is available using Google Calendar's FreeBusy API."""
    service = get_calendar_service()

    try:
        start_input = input("Enter start date and time (YYYY-MM-DD HH:MM AM/PM): ")
        end_input = input("Enter end date and time (YYYY-MM-DD HH:MM AM/PM): ")

        start_time = datetime.strptime(start_input, "%Y-%m-%d %I:%M %p").isoformat() + "Z"
        end_time = datetime.strptime(end_input, "%Y-%m-%d %I:%M %p").isoformat() + "Z"

        request_body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [{"id": "primary"}]
        }

        response = service.freebusy().query(body=request_body).execute()
        busy_slots = response.get("calendars", {}).get("primary", {}).get("busy", [])

        if not busy_slots:
            print("✅ Time slot is available.")
        else:
            print("❌ Time slot is NOT available.")
            for slot in busy_slots:
                print(f"⏳ Busy: {slot['start']} to {slot['end']}")

    except ValueError:
        print("❌ Invalid date format. Please enter the date in 'YYYY-MM-DD HH:MM AM/PM' format.")
    except Exception as e:
        print(f"❌ Error checking availability: {e}")


# ---------------------- CREATE EVENT WITH ATTACHMENT ---------------------- #
def create_event_with_attachment():
    """Creates an event with a Google Drive attachment and user-input date/time."""
    service = get_calendar_service()
    summary = input("Enter event title: ")
    file_url = input("Enter Google Drive file URL: ")
    timezone = input("Enter your time zone (e.g., Europe/London, Asia/Kolkata): ").strip()
    try:
        start_input = input("Enter start date and time (YYYY-MM-DD HH:MM AM/PM): ")
        end_input = input("Enter end date and time (YYYY-MM-DD HH:MM AM/PM): ")

        user_timezone = pytz.timezone(timezone)
        start_time = user_timezone.localize(datetime.strptime(start_input, "%Y-%m-%d %I:%M %p")).isoformat()
        end_time = user_timezone.localize(datetime.strptime(end_input, "%Y-%m-%d %I:%M %p")).isoformat()

        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': timezone},
            'end': {'dateTime': end_time, 'timeZone': timezone},
            'attachments': [{'fileUrl': file_url, 'title': 'Attachment'}],
        }

        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f"✅ Event created successfully!")
        print(f"📅 Event ID: {created_event.get('id')}")
        print(f"📍 Event Link: {created_event.get('htmlLink')}")

    except ValueError:
        print("❌ Invalid date format. Please enter the date in 'YYYY-MM-DD HH:MM AM/PM' format.")
    except pytz.UnknownTimeZoneError:
        print("❌ Invalid time zone. Please enter a valid time zone like 'Europe/London'.")

# ---------------------- CREATE EVENT WITH GOOGLE MEET ---------------------- #
def create_event_with_meet():
    """Creates an event with a Google Meet link and user-input date/time with timezone."""
    service = get_calendar_service()
    summary = input("Enter event title: ")
    timezone = input("Enter your time zone (e.g., Asia/Kolkata, Europe/London): ").strip()
    try:
        start_input = input("Enter start date and time (YYYY-MM-DD HH:MM AM/PM): ")
        end_input = input("Enter end date and time (YYYY-MM-DD HH:MM AM/PM): ")
        user_timezone = pytz.timezone(timezone)
        start_time = user_timezone.localize(datetime.strptime(start_input, "%Y-%m-%d %I:%M %p")).isoformat()
        end_time = user_timezone.localize(datetime.strptime(end_input, "%Y-%m-%d %I:%M %p")).isoformat()
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
        created_event = service.events().insert(
            calendarId=CALENDAR_ID, body=event, conferenceDataVersion=1
        ).execute()
        print(f"✅ Event created successfully!")
        print(f"📅 Event ID: {created_event.get('id')}")
        print(f"📍 Event Link: {created_event.get('htmlLink')}")
        print(f"🎥 Google Meet Link: {created_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', 'No Meet link generated')}")
    except ValueError:
        print("❌ Invalid date format. Please enter the date in 'YYYY-MM-DD HH:MM AM/PM' format.")
    except pytz.UnknownTimeZoneError:
        print("❌ Invalid time zone. Please enter a valid time zone like 'Asia/Kolkata' or 'Europe/London'.")
    except Exception as e:
        print(f"❌ Error creating event: {e}")
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

# ---------------------- CREATE FOCUS TIME EVENT ---------------------- #
def create_focus_time_event():
    """Creates a 'Focus Time' equivalent event (regular busy event)."""
    service = get_calendar_service()

    summary = input("Enter Focus Time event title: ")
    start_input = input("Enter start date and time (YYYY-MM-DD HH:MM AM/PM): ")
    end_input = input("Enter end date and time (YYYY-MM-DD HH:MM AM/PM): ")

    # Convert input to ISO 8601 format
    start_time = datetime.strptime(start_input, "%Y-%m-%d %I:%M %p").isoformat() + "Z"
    end_time = datetime.strptime(end_input, "%Y-%m-%d %I:%M %p").isoformat() + "Z"

    event = {
        "summary": summary,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
        "transparency": "opaque",  
        "visibility": "private",
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"✅ 'Focus Time' event created as a regular busy event: {created_event.get('htmlLink')}")

# ---------------------- CREATE OUT OF OFFICE EVENT ---------------------- #
def create_out_of_office_event():
    """Creates an 'Out of Office' equivalent event (regular busy event)."""
    service = get_calendar_service()

    summary = "Out of Office"
    start_input = input("Enter start date and time (YYYY-MM-DD HH:MM AM/PM): ")
    end_input = input("Enter end date and time (YYYY-MM-DD HH:MM AM/PM): ")

    # Convert input to ISO 8601 format
    start_time = datetime.strptime(start_input, "%Y-%m-%d %I:%M %p").isoformat() + "Z"
    end_time = datetime.strptime(end_input, "%Y-%m-%d %I:%M %p").isoformat() + "Z"

    event = {
        "summary": summary,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
        "transparency": "opaque",  # Marks the time as busy
        "visibility": "public",
        "description": "I will be out of office during this time.",
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"✅ 'Out of Office' event created as a regular busy event: {created_event.get('htmlLink')}")

# ---------------------- SET WORKING LOCATION ---------------------- #
def set_working_location():
    """Creates a regular all-day event to represent a working location."""
    service = get_calendar_service()

    location = input("Enter working location (e.g., 'Home', 'Office', 'Remote'): ")
    date_input = input("Enter the date (YYYY-MM-DD): ")

    event = {
        "summary": f"Working from {location}",
        "start": {"date": date_input},
        "end": {"date": date_input},  # End date must be the same for all-day event
        "visibility": "private",
        "description": f"📍 Working from {location} on {date_input}.",
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"✅ Working Location event created as a normal all-day event: {created_event.get('htmlLink')}")

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
        "17": ("Create Focus Time Event", create_focus_time_event),
        "18": ("Create Out of Office Event", create_out_of_office_event),
        "19": ("Set Working Location", set_working_location),
        "20": ("Exit", exit)
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
