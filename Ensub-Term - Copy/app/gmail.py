import os.path
import pickle
import re
import base64
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from collections import defaultdict

from email import message_from_bytes



#Returns a list of email_ids
def email_ids(service, sender):
    email_ids = []
    try:
        query = f'from:{sender}'
        results = service.users().messages().list(userId="me", q=query).execute()

        if("messages" in results):
            for message in results["messages"]:
                email_ids.append(message["id"])
            
        while("nextPageToken" in results):
            results = service.users().messages.list(userId="me", q=query, pageToken=results["nextPageToken"]).execute()
            if(message in results):
                for message in results["messages"]:
                    email_ids.append(message["id"])
    except Exception as e:
        print(f'{e}')
    
    return email_ids

#Returns a dictionary, the keys being different attributes and the values being their information. Ex. key: title, value: "interview..."
def single_email_info(service, email_id):
    try:
        #Generates an email with the given email_id so information can be extracted and relayed to a user when they select this specific email_id.
        email = service.users().messages().get(userId="me", id=email_id, format="full").execute()
        email_info = {}
        headers = email.get("payload", {}).get("headers", [])
        
        #Iterates through every possible header and determines if the values that are being looked for are included in the email. If so, they are assigned to their respective key value.
        email_info["title"] = next((header["value"] for header in headers if header["name"] == "Subject"), "No Subject")
        email_info["from"] = next((header["value"] for header in headers if header["name"] == "From"), "Unknown Sender")
        email_info["date_sent"] = next((header["value"] for header in headers if header["name"] == "Date"), "Unknown Date")
        email_info["is_starred"] = email.get("labelIds", [])
        if email.get("labelIds",[]).count("STARRED") > 0:
            email_info["is_starred"] = True
        else:
            email_info["is_starred"] = False

        #Assigns the "body" key to the text included in the email.
        parts = email.get("payload", {}).get("parts", [])
        body = None
        
        for part in parts:
            if part.get("mimeType") == "text/plain":
                body = base64.urlsafe_b64decode(part.get("body", {}).get("data", "")).decode("utf-8")
                break
        
        if not body:
            body = "No Body"
        
        email_info["body"] = body

        return email_info

    except Exception as e:
        print(f'{e}')
        return None

#Returns a dictionary, the keys being different senders and the valeus being the number of emails from that specific sender. Ex. key: "Nike" value: 231
def get_num_from_sender(service):
    sender_dict = defaultdict(int)

    try:
        #fetches all email IDs and assigns the list to messages
        messages = []
        results = service.users().messages().list(userId="me").execute()
        messages.extend(results.get("messages", []))

        #In the case of having more than one page of emails, the list of emails is contiuously added to messages
        while("nextPageToken" in results):
            results = service.users().messages().list(userId="me", pageToken=results["nextPageToken"]).execute()
            messages.extend(results.get("messages", []))
        

        for msg in messages:
            msg_id = msg["id"]
            message = service.users().messages().get(userId="me", id=msg_id, format="metadata").execute()

            #Exracts every single header in the list of messages. Iterates through each header and finds the from header which contains information regarding who sent the email. 
            headers = message.get("payload", {}).get("headers",[])
            from_header = next((header["value"] for header in headers if header["name"] == "From"), None)

            #If there is a header, then the specifc header can contain both the sender's name and email however, only the email is necessary. This extracts only the email and increments the email's key value in the dictionary.
            if(from_header):
                match = re.search(r'<(.*?)>', from_header)
                sender_email = match.group(1) if match else from_header
                sender_dict[sender_email] += 1                
                                

    except Exception as e:
        print(f'{e} - get_num_from_sender')
        
    
    return dict(sorted(sender_dict.items(), key = lambda item: item[1], reverse = True))



#Returns a boolean determing whether or not the input email is starred or not.
def is_starred(service, email_id):
    try:
        email = service.users().messages().get(userId="me", id=email_id, format="metadata").execute()
        label_ids = email.get("labelIds", [])
        return "STARRED" in label_ids
    except Exception as e:
        print(f'{e}')
        return False


#Boolean method that removes an email from a user's inbox.
def delete(service, email_id):
    try:
        service.users().messages().trash(userId="me", id=email_id).execute()
        return True
    except Exception as e:
        print(f'{e}')
        return False


def mass_delete_from_sender(service, sender_email, delete_starred):
    try:
        query = f'from:{sender_email}'
        next_page_token = None
        success = 0
        failure = 0
        starred = 0
        results = service.users().messages().list(userId="me", q=query).execute()
        
        while True:
            results = service.users().messages().list(userId="me", q=query, pageToken=next_page_token, maxResults=100).execute()

            messages = results.get("messages", [])
            
            if not messages:
                if next_page_token is None:
                    print(f'No emails found from {sender_email}')
                break

    

            print(f'Processing {len(messages)} emails from {sender_email}. Starting to delete now...')
        

            if delete_starred:
                for message in messages:
                    email_id = message["id"]
                    if delete(service, email_id):
                        success += 1
                    else:
                        failure += 1
            else:
                for message in messages:
                    email_id = message["id"]
                    if not is_starred(service, email_id):
                        if delete(service, email_id):
                            success += 1
                        else:
                            failure += 1
                    else:
                        starred += 1
            
            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break
        
        print(f"Mass deletion complete. Success: {success}, Failed: {failure}, Starred: {starred}")
        return (success, failure)

    except Exception as e:
        print(f'Error - mass Deletion: {e}')
        return (0,0)
    
