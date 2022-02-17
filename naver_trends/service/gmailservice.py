import os.path
import base64
from email.mime.text import MIMEText
from naver_trends.common.uinfo import OAUTHPATH, TOKENPATH
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from datetime import datetime

class GmailService:
    def __init__(self):
        self.scopes   = ['https://www.googleapis.com/auth/gmail.send']
        self.sender   = 'data@enzinex.com'
        self.receiver = 'justin@enzinex.com'
        self.msgbox   = []
        self.tag      = 'succeeded'

    def write_message(self, text):
        self.msgbox.append(text)
        return text

    def create_message(self):
        message = MIMEText('\n'.join(self.msgbox))
        message['from'] = self.sender
        message['to'] = self.receiver
        message['subject'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} NST Results : ' + self.tag
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_message(self):
        message = self.create_message()

        creds = None
        if os.path.exists(TOKENPATH):
            creds = Credentials.from_authorized_user_file(TOKENPATH, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(OAUTHPATH, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(TOKENPATH, 'w') as token:
                token.write(creds.to_json())
                
        try:
            gmail = build('gmail', 'v1', credentials=creds)
            results = gmail.users().messages().send(userId='me', body=message).execute()
            label = results.get('labelIds', [])

            if label == ['SENT']:
                return True
            else:
                return False
        except Exception as e:
            print(f'message send failed, error: {e}')