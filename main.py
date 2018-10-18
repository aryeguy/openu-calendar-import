# TODO parse example html using HTML parser
# TODO decide on parser
# TODO connect to google calendar API and create event for each study session
from lxml import html
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os

SCOPES = 'https://www.googleapis.com/auth/calendar'

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(os.environ['CREDENTIALS_PATH'], SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

# Call the Calendar API
now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

data = open('example.html', 'rb').read().decode("utf-8")
tree = html.fromstring(data)
table = tree.xpath('/html/body/table/tr[6]/td/table')[0]
for row in table.getchildren()[1:]:
    childrens = row.getchildren()
    if len(childrens) > 1:
        time_str = childrens[3].getchildren()[0].text.strip()
        date_str = childrens[4].getchildren()[0].text.strip()
        start, end = time_str.split('-')
        start = start.strip()
        end = end.strip()
        month, day, year = date_str.split('.')
        start_date = f'{year}-{day}-{month}T{start}:00-07:00'
        end_date = f'{year}-{day}-{month}T{end}:00-07:00'
        print(f'Meeting at {start_date} on {end_date}')
        
        event = {
            'summary': 'Logics study session',
            'start': {
                'dateTime': start_date,
                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'dateTime': end_date,
                'timeZone': 'Asia/Jerusalem',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        # print 'Event created: %s' % (event.get('htmlLink'))
# print('Getting the upcoming 10 events')
# events_result = service.events().list(calendarId='primary', timeMin=now,
#                                     maxResults=10, singleEvents=True,
#                                     orderBy='startTime').execute()
# events = events_result.get('items', [])
