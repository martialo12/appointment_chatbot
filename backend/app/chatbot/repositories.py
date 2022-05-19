import os
import pickle
import base64
from typing import Optional, List, Callable
import logging
from contextlib import AbstractAsyncContextManager
from datetime import datetime

from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
import google_auth_oauthlib.flow
from oauth2client import client
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi import Request as FastApiRequest

from .models import GoogleCredentials
from .schemas import CreateGoogleCredentials, GoogleCredentialsSchema
from app.core import config


logger = logging.getLogger(__name__)

PATH_TO_CREDS_FOLDER = os.path.join(os.getcwd(), "app/core")
PATH_TO_CLIENT_SECRETS_FILE = PATH_TO_CREDS_FOLDER + "/client_secrets.json"
PROFILE_INFO_URL = "https://www.googleapis.com/userinfo/v2/me"

USER_DICT = dict()


class GoogleCredentialsRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory

    async def create_google_credentials(
        self, create_google_credentials: CreateGoogleCredentials
    ) -> GoogleCredentialsSchema:

        # unique_identifier = str(uuid4())

        gcred = GoogleCredentials(
            name=create_google_credentials.name,
            email=create_google_credentials.email,
            timezone=create_google_credentials.timezone,
            access_token=create_google_credentials.access_token,
            refresh_token=create_google_credentials.refresh_token,
        )

        async with self.session_factory() as session:
            session.add(gcred)
            session.commit()
            session.refresh(gcred)

            gcred_id = gcred.id
            logger.debug(f"gcred_id: {gcred_id}")

            google_cred = (
                session.query(GoogleCredentials)
                .filter(GoogleCredentials.id == gcred_id)
                .first()
                .__dict__
            )
            # postgresql_user = postgresql_user.__dict__
            logger.debug(f"google_cred: {google_cred}")

            goo_cred = GoogleCredentials(
                name=google_cred["name"],
                email=google_cred["email"],
                timezone=google_cred["timezone"],
                access_token=google_cred["access_token"],
                refresh_token=google_cred["refresh_token"],
                created_at=google_cred["created_at"],
            )

            return goo_cred

    async def get_all_google_credentials(
        self,
    ) -> Optional[List[GoogleCredentialsSchema]]:
        async with self.session_factory() as session:
            all_gcreds = session.query(GoogleCredentials).all()
            return all_gcreds

    async def get_google_credentials_by_email(
        self, email: str
    ) -> Optional[GoogleCredentialsSchema]:
        async with self.session_factory() as session:
            gcreds = (
                session.query(GoogleCredentials)
                .filter(GoogleCredentials.email == email)
                .first()
            )
            if gcreds is None:
                return None
            return gcreds

    async def create_user_if_not_exist(
        self, user_info: dict
    ) -> Optional[GoogleCredentialsSchema]:
        async with self.session_factory():
            gcreds = await self.get_google_credentials_by_email(user_info["email"])
            if gcreds is None:
                create_google_credentials = CreateGoogleCredentials(
                    name=user_info["name"],
                    email=user_info["email"],
                    access_token=GoogleCredentialsRepository.base64_encode(
                        user_info["access_token"]
                    ),
                    refresh_token=GoogleCredentialsRepository.base64_encode(
                        user_info["refresh_token"]
                    ),
                )
                gcreds = await self.create_google_credentials(create_google_credentials)
                return gcreds
            return gcreds

    @staticmethod
    def base64_encode(token: str) -> str:
        token_string_bytes = token.encode("ascii")
        base64_bytes = base64.b64encode(token_string_bytes)
        base64_string = base64_bytes.decode("ascii")
        return base64_string

    @staticmethod
    def base_decode(token: str) -> str:
        base64_bytes = token.encode("ascii")
        token_string_bytes = base64.b64decode(base64_bytes)
        token_string = token_string_bytes.decode("ascii")
        return token_string

    @staticmethod
    async def authorize(request: FastApiRequest) -> RedirectResponse:
        # Use the client_secret.json file to identify the application requesting
        # authorization. The client ID (from that file) and access scopes are required.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            PATH_TO_CLIENT_SECRETS_FILE, scopes=config.CHATBOT_SCOPES
        )

        # The URI created here must exactly match one of the authorized redirect URIs
        # for the OAuth 2.0 client, which you configured in the API Console. If this
        # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
        # error.
        flow.redirect_uri = request.url_for("oauth2callback")
        # flow.redirect_uri = RedirectResponse(url="/oauth2callback", status_code=302)

        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type="offline",
            prompt="consent",
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes="true",
        )

        request.state.authorization_url = authorization_url
        request.session["state"] = state
        logger.debug(f"authorization_url-authorize: {request.state.authorization_url }")
        global USER_DICT
        USER_DICT["authorization_url"] = authorization_url
        return RedirectResponse(url=authorization_url, status_code=302)

    @staticmethod
    async def oauth2callback(request: FastApiRequest) -> RedirectResponse:
        # Specify the state when creating the flow in the callback so that it can
        # verified in the authorization server response.
        session = request.session
        state = session["state"]

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            PATH_TO_CLIENT_SECRETS_FILE, scopes=config.CHATBOT_SCOPES, state=state
        )

        flow.redirect_uri = request.url_for("oauth2callback")
        logger.debug(f"flow.redirect_uri: {flow.redirect_uri}")

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorizaton_response = request.query_params.get("code")
        logger.debug(f"request.url._url: {request.url._url}")
        logger.debug(f"request.url._url.code: {request.query_params.get('code')}")
        flow.fetch_token(code=authorizaton_response)

        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        credentials = flow.credentials
        creds_to_dict = GoogleCredentialsRepository.credentials_to_dict(credentials)
        logger.debug(f"creds_to_dict: {creds_to_dict}")
        request.session["creds_to_dict"] = creds_to_dict
        # request.session['credentials'] = credentials
        logger.debug(f"credentials- type: {type(credentials)}")
        card_profile = GoogleCredentialsRepository.get_user_info_from_google(
            credentials
        )
        logger.debug(f"card_profile: {card_profile}")
        request.session["user"] = card_profile
        global USER_DICT
        request.cookies["user"] = card_profile
        # request.cookies["authorization_url"] = authorization_url
        # request.session['authorization_url'] = USER_DICT['authorization_url']
        # logger.debug(f"session-oauth2callback: {request.session }")
        # logger.debug(f"authorization_url-oauth2callback: {request.state.authorization_url }")
        response = RedirectResponse(url="/accueil", status_code=302)
        response.set_cookie(
            key="authorization_url", value=USER_DICT["authorization_url"]
        )
        response.set_cookie(key="user", value=card_profile)
        response.set_cookie(key="token_uri", value=credentials.token_uri)
        response.set_cookie(key="client_id", value=credentials.client_id)
        response.set_cookie(key="client_secret", value=credentials.client_secret)
        response.set_cookie(key="creds", value=credentials)
        logger.debug(f"cookies-oauth2callback: {request.cookies }")

        return response

    @staticmethod
    def get_creds_from_google() -> Credentials:
        creds = None
        save_credential = True

        path_pickle = os.path.join(PATH_TO_CREDS_FOLDER, "token.pickle")
        if os.path.exists(path_pickle):
            with open(path_pickle, "rb") as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.warning("refreshing token...")
                creds.refresh(Request())
                logger.debug(f"refresh token: {creds.refresh_token}")
            else:
                # we authenticate user using client secrets file
                logger.debug(f"json file: {PATH_TO_CLIENT_SECRETS_FILE}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    PATH_TO_CLIENT_SECRETS_FILE, scopes=config.CHATBOT_SCOPES
                )
                creds = flow.run_local_server()
                logger.debug(f"token: {creds.token}")
                logger.debug(f"refresh token: {creds.refresh_token}")

        # Save the credentials for the next run
        if save_credential:
            logger.debug(f"token: {creds.token}")
            logger.debug(f"refresh token: {creds.refresh_token}")
            with open(PATH_TO_CREDS_FOLDER + "/token.pickle", "wb") as token:
                pickle.dump(creds, token)

        return creds

    @staticmethod
    def get_user_info_from_google(creds: Credentials) -> dict:
        service = build("oauth2", "v2", credentials=creds, cache_discovery=False)
        user_info = service.userinfo().get().execute()
        user_info["name"] = user_info["name"].replace(" (IT)", "")
        user_info["token_uri"] = creds.token_uri
        user_info["client_id"] = creds.client_id
        user_info["client_secret"] = creds.client_secret
        if creds.refresh_token:
            user_info["refresh_token"] = creds.refresh_token
        else:
            user_info["refresh_token"] = None
        user_info["access_token"] = creds.token
        logger.debug(f"profile_info: {user_info}")
        return user_info

    @staticmethod
    def get_all_events_from_calendar(creds: Credentials) -> JSONResponse:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        try:
            page_token = None
            while True:
                now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
                logger.debug(f"datetime now: {now}")
                events = (
                    service.events()
                    .list(
                        calendarId=config.CALENDAR_ID,
                        pageToken=page_token,
                        timeMin=now,
                        singleEvents=True,
                    )
                    .execute()
                )
                if not events:
                    logger.info("No upcoming events found.")
                    response = JSONResponse(
                        content=jsonable_encoder(
                            {"events": "No upcoming events found."}
                        )
                    )
                    return response
                else:
                    response = JSONResponse(
                        content=jsonable_encoder({"events": events})
                    )
                    return response

        except client.AccessTokenRefreshError:
            logger.warning(
                "The credentials have been revoked or expired, please re-run"
                "the application to re-authorize."
            )

    @staticmethod
    def get_service_calendar(creds: Credentials) -> Resource:
        service_calendar = build(
            "calendar", "v3", credentials=creds, cache_discovery=False
        )
        return service_calendar

    @staticmethod
    def credentials_to_dict(creds: Credentials) -> dict:
        return {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

    @staticmethod
    def produce_profile_message(creds: Credentials) -> dict:
        """Generate a message containing the users profile inforamtion."""
        oauth2_client = build("oauth2", "v2", credentials=creds)
        user_info = oauth2_client.userinfo().get().execute()  # THIS FAILS
        return user_info
