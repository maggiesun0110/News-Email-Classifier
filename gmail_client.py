#installed app flow does the signing in and granting local app permission
#build creates client object to call Gmail
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def get_gmail_service():
    creds = None

    #the what access do you want screen
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    #refresh or auth if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        #save newly auth or refresehed
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service

def fetch_email(service, message_id):

    email_data = service.users().messages().get(
        userId="me",
        id=message_id,
        format="metadata",
        metadataHeaders=["From", "Subject"]
    ).execute()

    headers = email_data["payload"]["headers"]

    sender = ""
    subject = ""

    for header in headers:
        if header["name"] == "From":
            sender = header["value"]
        elif header["name"] == "Subject":
            subject = header["value"]

    snippet = email_data.get("snippet", "")

    email = {
        "message_id": message_id,
        "thread_id": email_data["threadId"],
        "sender": sender,
        "subject": subject,
        "snippet": snippet
    }

    return email

if __name__ == "__main__":
    service = get_gmail_service()

    #me is the account i authorized
    #labelIds limits search to inbox messages
    #maxresults requests at most one
    #.execute sends req
    response = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=1
    ).execute()

    messages = response.get("messages", [])

    if messages:
        message_id = messages[0]["id"]
        email = fetch_email(service, message_id)
        print(email)



