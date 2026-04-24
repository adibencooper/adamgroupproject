from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]

SERVICE_ACCOUNT_FILE = "credentials.json"

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

def getCalendarService():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credential=creds)

def getbusyTimes(starttime, endtime):
    service = getCalendarService()
    body = {
        "minTime": starttime,
        "maxTime": endtime,
        "timeZone": "UTC",
        "items": [{"id": CALENDAR_ID}],
    }
    result = service.freebusy().query(body=body).execute()
    return result["calendars"][CALENDAR_ID]["busy"]
    

def generateSlots(starttime, endtime, durationMins):
    busyTimes = getbusyTimes(starttime, endtime)
    start = parser.parse(starttime)
    end = parser.parse(endtime)

    slots = []
    current = start

    while current + timedelta(minutes=durationMins) <= end:
        slotEnd = current + timedelta(minutes=durationMins)

        overlap = False
        for b in busyTimes:
            busyStart = parser.parse(b["start"])
            busyEnd = parser.parse(b["end"])

            if current < busyEnd and slotEnd > busyStart:
                overlap = True
                break

            if not overlap:
                slots.append({"start": current.isoformat(), "end": slotend.isoformat()})

            current += timedelta(minutes=durationMins)

        return slots

def createEvent(starttime, endtime, summary, description):
    service = getCalendarService()

    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": starttime, "timeZone": "UTC"},
        "end": {"dateTime": endtime, "timeZone": "UTC"},
     }

    return service.events().insert(calendarId=CALENDAR_ID, body=event).execute()