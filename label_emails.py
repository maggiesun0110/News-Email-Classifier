import pandas as pd
from gmail_client import get_gmail_service, fetch_email
from pathlib import Path

def print_email(email):
    print("Sender:", email["sender"])
    print("Subject:", email["subject"])
    print("Snippet:", email["snippet"])

def ask_for_label():
    while True:
        choice = input("Filter this email? (1 = yes, 0 = no, q = quit): ")

        if choice == "0" or choice == "1":
            return int(choice)
        elif choice == "q":
            return None
        else:
            print("enter 1 or 0 or q")

#setup the api and client
service = get_gmail_service()


output_path = Path("new_labels.csv")

#checking if the output file exists
if output_path.exists():
    saved_labels = pd.read_csv(output_path, dtype={"message_id": str})
    labeled_ids = set(saved_labels["message_id"])
else:
    labeled_ids = set()

page_token = None
quit_requested = False

while True:
    response = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=10,
        pageToken=page_token
    ).execute()

#the response is a dictionary with a key "messages" that contains a list of message objects. Each message object has an "id" and a "threadId".
    messages = response.get("messages", [])

#checking if there are any messages in the inbox
    if messages:
        for message in messages:
            if message["id"] in labeled_ids:
                print("Already Labeled")
            else:
                email = fetch_email(service, message["id"])
                print_email(email)
                label = ask_for_label()
                if label is None:
                    quit_requested = True
                    break
                email["label"] = label
                new_row = pd.DataFrame([email])

                new_row.to_csv(
                    output_path,
                    mode="a",
                    header=not output_path.exists(),
                    index=False
                )

                labeled_ids.add(message["id"])

    if quit_requested:
        break
    
    page_token = response.get("nextPageToken")

    if not page_token:
        break
