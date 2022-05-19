"""Services chatbot module."""

from typing import Optional, List

from google.oauth2.credentials import Credentials
from starlette.responses import JSONResponse
from googleapiclient.discovery import Resource
from fastapi import Request as FastApiRequest
from fastapi.responses import RedirectResponse

from .repositories import GoogleCredentialsRepository
from .schemas import CreateGoogleCredentials, GoogleCredentialsSchema


class GoogleCredentialsService:
    def __init__(self, gcreds_repository: GoogleCredentialsRepository) -> None:
        self._repository: GoogleCredentialsRepository = gcreds_repository

    async def create_google_credentials(
        self, create_google_credentials: CreateGoogleCredentials
    ) -> GoogleCredentialsSchema:
        goo_cred = await self._repository.create_google_credentials(
            create_google_credentials
        )
        return goo_cred

    async def get_all_google_credentials(
        self,
    ) -> Optional[List[GoogleCredentialsSchema]]:
        all_gcreds = await self._repository.get_all_google_credentials()
        return all_gcreds

    async def get_google_credentials_by_email(
        self, email: str
    ) -> Optional[GoogleCredentialsSchema]:
        gcreds = await self._repository.get_google_credentials_by_email(email)
        return gcreds

    async def create_user_if_not_exist(
        self, user_info: dict
    ) -> Optional[GoogleCredentialsSchema]:
        gcreds = await self._repository.create_user_if_not_exist(user_info)
        return gcreds

    @staticmethod
    def get_creds_from_google() -> dict:
        user_data = GoogleCredentialsRepository.get_creds_from_google()
        return user_data

    @staticmethod
    def get_user_info_from_google(creds: Credentials) -> dict:
        user_info = GoogleCredentialsRepository.get_user_info_from_google(creds)
        return user_info

    @staticmethod
    def get_all_events_from_calendar(creds: Credentials) -> JSONResponse:
        events = GoogleCredentialsRepository.get_all_events_from_calendar(creds)
        return events

    @staticmethod
    def get_service_calendar(creds: Credentials) -> Resource:
        service_calendar = GoogleCredentialsRepository.get_service_calendar(creds)
        return service_calendar

    @staticmethod
    def credentials_to_dict(creds: Credentials) -> dict:
        creds_to_dict = GoogleCredentialsRepository.credentials_to_dict(creds)
        return creds_to_dict

    @staticmethod
    async def authorize(request: FastApiRequest) -> RedirectResponse:
        return await GoogleCredentialsRepository.authorize(request)

    @staticmethod
    async def oauth2callback(request: FastApiRequest) -> RedirectResponse:
        return await GoogleCredentialsRepository.oauth2callback(request)

    @staticmethod
    def produce_profile_message(creds: Credentials) -> dict:
        card_profile = GoogleCredentialsRepository.produce_profile_message(creds)
        return card_profile
