"""Endpoints auth module."""

import logging
import ast

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from google.oauth2.credentials import Credentials

from app.containers import Container
from .services import GoogleCredentialsService
from app.db.exceptions import (
    exception_handling,
)

# from app.user.schemas import InternalUser
from app.core.custom_lib.df_response_lib import (
    fulfillment_response,
    actions_on_google_response,
)
from app.core.custom_lib.webhookaction import WebhookAction

# from app.core import config
from .schemas import Action


logger = logging.getLogger(__name__)

chatbot = APIRouter(tags=["chatbot"])
user_info = None


@chatbot.get("/accueil")
@inject
async def test(
    request: Request,
    gcreds_service: GoogleCredentialsService = Depends(
        Provide[Container.gcreds_service]
    ),
):
    """This request sets parameters that identify your application and define the permissions
        that the user will be asked to grant to your application.

    Args:
        :Request: request: request object

    Returns:
        Redirect response to the external provider's auth endpoint
    """
    async with exception_handling():
        global user_info
        user_info = (
            ast.literal_eval(request.cookies.get("user"))
            if request.cookies.get("user")
            else None
        )
        authorization_url = request.cookies.get("authorization_url")
        # if request.state.authorization_url:
        #     authorization_url = request.state.authorization_url
        # logger.debug(f"authorization_url  - test: {authorization_url}")
        # user_info['authorization_url'] = authorization_url

        # creds = None
        if user_info:
            # authorization_url = request.state.authorization_url
            logger.debug(f"user_info - test- type: {type(user_info)}")
            logger.debug(f"user_info - test: {user_info}")
            logger.debug(f"authorization_url  - test: {authorization_url}")
            user_info["authorization_url"] = authorization_url
            # creds = Credentials(
            #     token=user_info["access_token"],
            #     refresh_token=user_info["refresh_token"]
            # )

        logger.debug(f"user_info - test: {user_info}")
        logger.debug(f"authorization_url  - test: {authorization_url}")
        if user_info:
            gcreds = await gcreds_service.create_user_if_not_exist(user_info)
            html = (
                f"<pre>{gcreds.email}</pre>"
                f'<pre>Ciao {user_info["given_name"]}</pre>'
                '<a href="/logout">logout</a>'
            )
            return HTMLResponse(html)
        return HTMLResponse('<a href="/authorize">login</a>')


@chatbot.post("/webhook")
@inject
async def webhook(
    # user: InternalUser,
    # internal_user: InternalUser = Depends(access_token_cookie_scheme),
    request: Request,
    gcreds_service: GoogleCredentialsService = Depends(
        Provide[Container.gcreds_service]
    ),
) -> dict:

    """This method handles the http requests for the Dialogflow webhook.
       webhook URL which we’ll provide as a Fulfillment URL in Dialogflow:
       During a conversation, fulfillment allows you to use the information
       extracted by Dialogflow’s natural language processing to generate dynamic
       responses or trigger actions on your back-end.

    Args:
        request:  request object coming from dialog flow

    Returns:
        dict: fulfillment response
        :param request:
        :param gcreds_service:
    """
    async with exception_handling():
        # user_info = ast.literal_eval(request.cookies.get('user')) if request.cookies.get('user') else None
        credentials = (
            request.cookies.get("creds") if request.cookies.get("creds") else None
        )
        logger.debug(f"credentials - webhook: {credentials}")
        global user_info
        logger.debug(f"user_info - webhook: {user_info}")
        authorization_url = request.cookies.get("authorization_url")
        # token_uri = request.cookies.get('token_uri')
        # logger.debug(f"token_uri: {token_uri}")
        # client_id = request.cookies.get('client_id')
        # client_secret = request.cookies.get('client_secret')
        service = None
        ful = fulfillment_response()
        aog = actions_on_google_response()
        req = await request.json()
        query_result = req["queryResult"]
        webhookAction = WebhookAction(
            query_result=query_result,
            service=service,
            ful=ful,
            aog=aog,
            user_info=user_info,
            request=request,
        )
        if user_info:
            logger.debug(f"user_info - test: {user_info}")
            logger.debug(f"authorization_url  - test: {authorization_url}")
            user_info["authorization_url"] = authorization_url
            creds = Credentials(
                token=user_info["access_token"],
                refresh_token=user_info["refresh_token"],
                token_uri=user_info["token_uri"],
                client_id=user_info["client_id"],
                client_secret=user_info["client_secret"],
            )
            service = gcreds_service.get_service_calendar(creds)
            logger.debug(f"service: {service}")
            query_result["parameters"]["email"] = user_info["email"]
            # fetch parameters
            logger.debug(f"service: {service}")
            webhookAction = WebhookAction(
                query_result=query_result,
                service=service,
                ful=ful,
                aog=aog,
                user_info=user_info,
                request=request,
            )
            # fetched “action” from the request using
            if query_result["action"] == Action.CREATE_MEETING:
                res = webhookAction.create_meeting()
                return res
            elif query_result["action"] == Action.GREETINGS:
                res = webhookAction.greetings()
                return res
        res = webhookAction.greetings()
        return res


@chatbot.get("/authorize")
@inject
async def authorize(
    # user: InternalUser,
    # internal_user: InternalUser = Depends(access_token_cookie_scheme),
    request: Request,
    gcreds_service: GoogleCredentialsService = Depends(
        Provide[Container.gcreds_service]
    ),
):
    """This request sets parameters that identify your application and define the permissions
        that the user will be asked to grant to your application.

    Args:
        :Request: request: request object

    Returns:
        Redirect response to the external provider's auth endpoint
    """
    async with exception_handling():
        return await gcreds_service.authorize(request)


@chatbot.get("/oauth2callback")
@inject
async def oauth2callback(
    # user: InternalUser,
    # internal_user: InternalUser = Depends(access_token_cookie_scheme),
    request: Request,
    gcreds_service: GoogleCredentialsService = Depends(
        Provide[Container.gcreds_service]
    ),
):
    """This request sets parameters that identify your application and define the permissions
        that the user will be asked to grant to your application.

    Args:
        :Request: request: request object

    Returns:
        Redirect response to the external provider's auth endpoint
    """
    async with exception_handling():
        return await gcreds_service.oauth2callback(request)
