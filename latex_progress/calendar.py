import os
import datetime
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
TOKEN_PATH = os.path.expanduser('~/.latex-progress.token.pickle')
CREDENTIALS_PATH = os.path.expanduser('~/.latex-progress.credentials.json')


def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
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


def create_event(summary, description, date, calendar_id='primary', timezone='Europe/Berlin'):
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
