import logging
from datetime import datetime

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from fastapi import Request

from app.core.custom_lib.df_response_lib import (
    fulfillment_response,
    actions_on_google_response,
)
from app.chatbot.schemas import Action

# from app.core import config

logger = logging.getLogger(__name__)


class WebhookAction:
    def __init__(
        self,
        query_result: dict,
        service: Resource,
        ful: fulfillment_response,
        aog: actions_on_google_response,
        user_info: dict,
        request: Request,
    ):
        self.query_result = query_result
        self.service = service
        self.ful = ful
        self.aog = aog
        self.user_info = user_info
        self.request = request

    def create_meeting(self) -> dict:
        try:
            emails_participants = set(
                self.query_result["parameters"]["emailparticipants"]
            )
            event_day = self.query_result["parameters"]["jourRDV"]
            start_date_time = self.query_result["parameters"]["heureDebut"]
            end_date_time = self.query_result["parameters"]["heureFin"]
            title = self.query_result["parameters"]["titre"]
            description = self.query_result["parameters"]["description"]
            logger.debug(f"emails_participants: {emails_participants}")
            logger.debug(f"event_day: {event_day}")
            logger.debug(f"start_date_time: {start_date_time}")
            logger.debug(f"end_date_time: {end_date_time}")
            logger.debug(f"title: {title}")
            logger.debug(f"description: {description}")
            logger.debug(f"query_result: {self.query_result['intent']['displayName']}")
            fufillment = []
            logger.debug(f"Action.CREATE_EVENT: {Action.CREATE_MEETING}")
            emails_participants.add(self.user_info["email"])
            logger.debug(f"emails_participants->: {emails_participants}")
            # d = datetime.now().date()
            # tomorrow = datetime(d.year, d.month, d.day, 10) + timedelta(days=1)
            # start = tomorrow.isoformat()
            # end = (tomorrow + timedelta(hours=1)).isoformat()
            # events = self.service.events().list(
            #     calendarId=config.CALENDAR_ID, singleEvents=True
            # ).execute()

            body = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start_date_time, "timeZone": "Europe/Rome"},
                "end": {"dateTime": end_date_time, "timeZone": "Europe/Rome"},
                "attendees": [
                    {"email": email.lower()} for email in emails_participants
                ],
                "conferenceData": {"createRequest": {"requestId": "SecureRandom.uuid"}},
            }
            event_result = (
                self.service.events()
                .insert(
                    calendarId="primary",
                    body=body,
                    sendUpdates="all",
                    conferenceDataVersion=1,
                )
                .execute()
            )
            start = datetime.fromisoformat(start_date_time).strftime("%d-%m-%Y %H:%M")
            end = datetime.fromisoformat(end_date_time).strftime("%d-%m-%Y %H:%M")
            logger.debug(f"start: {start}")
            logger.debug(f"end: {end}")
            event = f"""Le meeting intitulé: *{event_result["summary"]}* débutera: _{start}_,
             e terminera: _{end}_\n\n Merci <users/{self.user_info['id']}>! à la prochaine"""
            logger.debug(f"event: {event}")
            fufillment.append(event)
            res = self.ful.main_response(
                fulfillment_text=self.ful.fulfillment_text(event),
                fulfillment_messages=None,
                output_contexts=None,
                followup_event_input=None,
            )
            logger.debug(f"res: {res}")
            return res
        except HttpError as err:
            logger.error(f"something went wrong: {err}")
            error_message = """
            Je suis désolé, mais une erreur est survenue durant la création de la réunion.
            S'il te plait, recommence de nouveau.

            Merci.
            """
            res = self.ful.main_response(
                fulfillment_text=self.ful.fulfillment_text(error_message),
                fulfillment_messages=None,
                output_contexts=None,
                followup_event_input=None,
            )
            return res

    def greetings(self) -> dict:
        if self.user_info:
            logger.info(f"user_inf: {self.user_info}")
            # self.query_result['parameters']['email'] = self.user_info["email"]
            question = "J'espère que tu vas bien. Comment puis je t'aider?"
            res = self.ful.main_response(
                fulfillment_text=self.ful.fulfillment_text(
                    f"Bonjour **{self.user_info['given_name']}** \n {question}"
                ),
                fulfillment_messages=None,
                output_contexts=None,
                followup_event_input=None,
            )
            return res
        # self.query_result['parameters']['email'] = self.user_info["email"]
        question = "Spero stia bene. Come posso aiutarti?"
        # url = self.request.cookies.get('authorization_url')
        # logger.info(f"authorization url: {url}")
        res = self.ful.main_response(
            fulfillment_text=None,
            fulfillment_messages=self.ful.fulfillment_messages(
                [
                    self.aog.card(
                        title="Authentification",
                        subtitle="Salut, tu dois t'authentifier pour utiliser ce service",
                        buttons=[
                            "login",
                            "https://kwagchatbot.xyz/authorize",
                        ],
                        image=[
                            "https://e7.pngegg.com/pngimages/715/371/png-clipart-youtube-google-logo-google-s-google"
                            "-account-youtube-text-trademark.png",
                            "login",
                        ],
                    )
                ]
            ),
            # fulfillment_messages=self.ful.fulfillment_messages(
            #     self.aog.link_out_suggestion("devi autenticarti prima di usare il nostro servizio", url)),
            output_contexts=None,
            followup_event_input=None,
        )
        # res = self.response_card_message()
        return res
