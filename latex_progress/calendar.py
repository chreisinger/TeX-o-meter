from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle


SCOPES = ['https://www.googleapis.com/auth/calendar.events']
TOKEN_PATH = str(Path('~/.latex-progress.token.pickle').expanduser())
CREDENTIALS_PATH = str(Path('~/.latex-progress.credentials.json').expanduser())


def get_calendar_service():
    creds = None
    token_path = Path(TOKEN_PATH)
    if token_path.exists():
        with token_path.open('rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service


def create_event(summary, description, date, calendar_id='primary', timezone='Europe/Vienna'):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'date': date,
            'timeZone': timezone,
        },
        'end': {
            'date': date,
            'timeZone': timezone,
        },
    }
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return event


def upsert_event(summary, description, date, calendar_id='primary', timezone='Europe/Vienna'):
    """Create or update a calendar event for the given date (all-day)."""
    service = get_calendar_service()
    # Add a unique tag to the description for this date
    tag = f"<!--latex-progress:{date}-->"
    description_tagged = f"{description}\n{tag}"
    # Use RFC3339 with timezone offset for timeMin/timeMax
    from datetime import datetime, timedelta
    import pytz
    tz = pytz.timezone(timezone)
    dt_start = tz.localize(datetime.strptime(date, "%Y-%m-%d"))
    dt_end = dt_start + timedelta(days=1)
    time_min = dt_start.isoformat()
    time_max = dt_end.isoformat()
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    items = events_result.get('items', [])
    found = None
    for ev in items:
        desc = ev.get('description', '')
        if tag in desc:
            found = ev
            break
    event_body = {
        'summary': summary,
        'description': description_tagged,
        'start': {
            'date': date,
            'timeZone': timezone,
        },
        'end': {
            'date': date,
            'timeZone': timezone,
        },
    }
    if found:
        event_id = found['id']
        event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event_body).execute()
    else:
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
    return event


