import glob
import os, json, random
import pickle
import requests
from yaml import Loader
from yaml import load
from flickrapi import FlickrAPI
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import ParseMode,  ReplyKeyboardMarkup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.auth.transport.requests import Request

def get_google_album():
    print("get image from gg")
    scopes = ['https://www.googleapis.com/auth/photoslibrary.readonly']

    creds = None
    CREDENTIALS_FILE = 'credentials.pickle'

    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                scopes)
            creds = flow.run_local_server(port=8090)
            with open(CREDENTIALS_FILE, 'wb') as token:
                pickle.dump(creds, token)

    service = build('photoslibrary', 'v1', credentials=creds,static_discovery=False)

    albums_shared = service.sharedAlbums().list(
        pageSize=10).execute()

    list_album = albums_shared.get('sharedAlbums', [])
    # print(list_album)
    for album in list_album:
        if album["title"] == "gái xinh":
            album_id = album["id"]

    nextpagetoken = 'Dummy'
    c=0
    list_item=[]
    while nextpagetoken != '':
        print("wait.....")
        nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
        results = service.mediaItems().search(
                body={"albumId": album_id,
                    "pageSize": 100, "pageToken": nextpagetoken}).execute()
        # The default number of media items to return at a time is 25. The maximum pageSize is 100.
        items = results.get('mediaItems', [])
        nextpagetoken = results.get('nextPageToken', '')
        for item in items:
            c+=1
            # print(f"{c}\nURL: {item['productUrl']}")
            list_item.append(item['baseUrl'])
            # l.append(item['productUrl'])
    return list_item

get_google_album()