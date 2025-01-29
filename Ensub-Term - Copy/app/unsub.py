
import re
import base64
import requests




#Returns a boolean that represents whether or not the input email has an unsub link within the body of the email.
def contains_unsub_link(service, email_id):
    email = service.users().messages().get(userId="me", id=email_id, format="full").execute()
    parts = email.get("payload", {}).get("parts", [])
    body = None

    for part in parts:
        if part.get("mimeType") == "text/plain" or part.get("mimeType") == "text/html":
            body = base64.urlsafe_b64decode(part.get("body", {}).get("data", "")).decode("utf-8")
            break
    
    if body == None:
        return False
    
    return any(keyword in body.lower() for keyword in ["unsubscribe", "opt-out", "manage preferences"])


#Returns a boolean that represents whether or not the input email has an unsubscribe header button. If this is the case, then that means that the user must be subscribed to the sender.
def has_unsub_button(service, email_id):
    try:
        email = service.users().messages().get(userId="me", id=email_id, format="full").execute()
        headers = email.get("payload", {}).get("headers", [])
        sub_header = next((header["value"] for header in headers if header["name"].lower() == "list-unsubscribe"), None)
        if sub_header != None:
            return True
        else:
            return False
    
    except Exception as e:
        print(f'{e}')

#Returns a boolean representing if the user is subscribed to the input email.
#Uses "contains_unsub_link(service, email_id)" and "has_unsub_button(service, email_id)" as helper methods to determine whether or not the user is subscribed to the sender.
def is_subbed(service, email_id):
    try:
        if has_unsub_button(service, email_id) == True or contains_unsub_link(service, email_id) == True:
            return True
        else:
            return False
    except Exception as e:
        print(f'{e}')

#Returns a list of all senders that the user is subscribed to.
def all_subbed_senders(service):
    subscribed_senders = []
    next_page_token = None

    while True:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], pageToken=next_page_token, maxResults=100).execute()
        messages = results.get("messages", [])
        next_page_token = results.get("nextPageToken")

        for message_meta in messages:
            email = service.users().messages().get(userId="me", id=message_meta["id"], format="full").execute()
            headers = email.get("payload", {}).get("headers", [])

            from_header = next((header["value"] for header in headers if header["name"] == "From"), None)
            if not from_header:
                continue
            match = re.search(r'<(.*?)>', from_header)
            sender_email = match.group(1) if match else from_header

            if is_subbed(service, message_meta["id"]):
                if sender_email not in subscribed_senders:
                    subscribed_senders.append(sender_email)
                    
        
        if not next_page_token:
            break
    
    return subscribed_senders



#Void method that unsubscribes from an input sender.
def unsub_from_sender(service, sender):
    try:
        query = f'from:{sender}'
        results = service.users().messages().list(userId="me", q=query, maxResults=1).execute()
        messages = results.get("messages", [])

        if not messages:
            print(f'No emails found from {sender}')
            return False
        
        email_id = messages[0]["id"]
        email = service.users().messages().get(userId="me", id=email_id, format="full").execute()

        headers = email.get("payload", {}).get("headers",[])
        unsub_header = next((header["value"] for header in headers if header["name"] == "List-Unsubscribe"), None)

        if unsub_header:
            if "<" in unsub_header and ">" in unsub_header:
                unsub_url = unsub_header.strip("<>")
                response = requests.get(unsub_url)
                if response.status_code == 200:
                    print(f'Succesfully unsubscribed from {sender} using List-Unsub')
                    return True
                else:
                    print(f'Failed to unsub by List-Unsub')
            elif "mailto:" in unsub_header:
                print(f'Mailto-based unsubscribe detected for {sender}')
    
        print(f'No unsub method found for {sender}')
        return False

    except Exception as e:
        print(f'{e}')
        return False
        

