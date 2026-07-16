import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_info = json.loads(os.environ["GMAIL_TOKEN_JSON"])
creds = Credentials.from_authorized_user_info(token_info)
service = build("gmail", "v1", credentials=creds)

request = {
    "labelIds": ["INBOX"],
    "topicName": "projects/placement-email-alerts/topics/gmail-notifications"
}

response = service.users().watch(userId="me", body=request).execute()
print(response)