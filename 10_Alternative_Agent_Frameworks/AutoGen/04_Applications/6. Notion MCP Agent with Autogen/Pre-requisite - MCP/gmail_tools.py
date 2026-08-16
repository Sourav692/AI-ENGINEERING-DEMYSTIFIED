import os
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

# Set up Gmail API credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service(token_path: str, credentials_path: str):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file('Bearer ' + str(token_path), SCOPES)
    if not creds or not creds.valid:
        raise Exception("Valid Gmail API credentials required.")
    return build('gmail', 'v1', credentials=creds)

def read_emails(service, user_id: str = 'me', query: str = '', max_results: int = 5) -> List[Dict]:
    results = service.users().messages().list(userId=user_id, q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        msg_data = service.users().get(userId=user_id, id=msg['id'], format='full').execute()
        payload = msg_data.get('payload', {})
        headers = payload.get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_ = next((h['value'] for h in headers if h['name'] == 'From'), '')
        snippet = msg_data.get('snippet', '')
        emails.append({'id': msg['id'], 'from': from_, 'subject': subject, 'snippet': snippet})
    return emails

def create_message(to: str, subject: str, body: str) -> dict:
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(service, to: str, subject: str, body: str, user_id: str = 'me') -> dict:
    message = create_message(to, subject, body)
    sent = service.users().messages().send(userId=user_id, body=message).execute()
    return sent

def draft_email(service, to: str, subject: str, body: str, user_id: str = 'me') -> dict:
    message = create_message(to, subject, body)
    draft = service.users().drafts().create(userId=user_id, body={'message': message}).execute()
    return draft

def delete_email():
    pass

def recover_email(service, user_id: str = 'me', message_id: str = '') -> dict:
    pass


# Example usage:
# service = get_gmail_service('token.json', 'credentials.json')
# emails = read_emails(service, query='is:unread', max_results=3)
# send_email(service, 'recipient@example.com', 'Subject', 'Body text')
# draft_email(service, 'recipient@example.com', 'Draft Subject', 'Draft body')