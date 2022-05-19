from __future__ import print_function
import os
import os.path
import logging
from typing import List

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path


logger = logging.getLogger(__name__)

load_dotenv()
SECRET_FILE = os.getenv("SECRET_FILE")
logger.debug(f"SECRET FILE: {SECRET_FILE}")
# If modifying these scopes, delete the file token.json.
SCOPES = os.getenv("SCOPES")
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SAMPLE_SPREADSHEET_ID")
SAMPLE_RANGE_NAME = os.getenv("SAMPLE_RANGE_NAME")


class IntentManagement:
    def __init__(self, secret_file, scopes):
        self.service = self.get_sheet_service(secret_file, scopes)

    def get_sheet_service(self, secret_file, scopes):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                secret_json_file = Path(__file__).parent.parent / secret_file
                flow = InstalledAppFlow.from_client_secrets_file(
                    secret_json_file, scopes
                )
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("sheets", "v4", credentials=creds)
            return service
        except HttpError as err:
            logger.error(
                f"Something went wrong trying to et the shets service API: {err}"
            )

    def get_message_texts_from_sheet_file(self) -> List[str]:
        # Call the Sheets API
        sheet = self.service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])
        if not values:
            logger.warning("No data found.")
            return []
        message_texts = []
        for row in values:
            message_texts.append(row[0].lower())
        logger.info(f"all message texts are: \n {message_texts}")
        return message_texts

    def get_training_phrases_parts_from_sheet_file(self):
        parts = ("evento", "meeting", "riunione", "meet", "incontro")
        return parts
