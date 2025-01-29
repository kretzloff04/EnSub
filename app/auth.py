import os
import pickle
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

from flask import redirect, request, url_for, session





CLIENT_FILE = "client.json"
SCOPES = ["https://mail.google.com/", "openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
CLIENT_ID = "***"
CLIENT_SECRET_ID = "***"
REDIRECT_URI = "http://localhost:5000/oauth2callback"




 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



def create_gmail_service():
  
    creds = None
    # Token file to store user credentials after authorization
    token_file = 'token.pickle'

    # Load saved credentials if they exist
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If credentials are not available or are invalid, prompt user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI)
            creds = flow.run_local_server(port=5000)
            

        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service


def google_login():
    flow = Flow.from_client_secrets_file(CLIENT_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI)

    if "code" not in request.args:
        auth_url, _ = flow.authorization_url(prompt="consent")
        print("Generated auth URL:", auth_url)
        return redirect(auth_url)
    
    print("OAuth callback with code received")  # Debugging
    flow.fetch_token(authorization_response=request.url)
    

    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(credentials.id_token, requests.Request(), CLIENT_ID)

    user_info = {
        "id" : id_info["sub"],
        "email" : id_info["email"],
        "name" : id_info.get("name"),
        "picture" : id_info.get("picture")
    }
    
    return user_info

def google_logout():
    session.clear()
