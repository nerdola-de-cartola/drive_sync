import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PICKLE = 'token.pickle'
CREDENTIALS_JSON = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    # Load saved credentials from token.pickle
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token_file:
            creds = pickle.load(token_file)

    # If no valid credentials, authenticate user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for next run
        with open(TOKEN_PICKLE, 'wb') as token_file:
            pickle.dump(creds, token_file)

    # Build the Drive service
    service = build('drive', 'v3', credentials=creds)
    return service


def main():
    pass

if __name__ == "__main__":
    main()
