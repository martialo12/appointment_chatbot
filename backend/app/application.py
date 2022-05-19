"""Application module."""
import os
import logging.config

from fastapi import FastAPI, Request, status

# from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.middleware.sessions import SessionMiddleware

from app.containers import Container
from app.chatbot import endpoints as chatbot_endpoints
from app.core import config

logging.config.fileConfig(
    os.path.join(os.getcwd(), "app/core/logging.ini"),
    disable_existing_loggers=False,
)
# create logger
logger = logging.getLogger("chatbot")
logger.info("Starting up Nudge Backend System...")
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


def create_app() -> FastAPI:
    container = Container()
    # container.config.from_yaml("./../docker-compose.yml")
    container.config.from_yaml("config.yml")
    container.wire(modules=[chatbot_endpoints])

    db = container.db()
    db.create_database()

    my_app = FastAPI(title=config.PROJECT_TITLE, version=config.PROJECT_VERSION)

    # Allows CORS. DON'T do that on production!
    # origins = ["*"]

    my_app.add_middleware(
        # CORSMiddleware,
        SessionMiddleware,
        # allow_origins=origins,
        # allow_credentials=True,
        # allow_methods=["*"],
        # allow_headers=["*"],
        secret_key="!secret",
    )

    @my_app.middleware("http")
    async def setup_request(request: Request, call_next) -> JSONResponse:
        """
        A middleware for setting up a request. It creates a new request_id
        and adds some basic metrics.

        Args:
            request: The incoming request
            call_next (obj): The wrapper as per FastAPI docs

        Returns:
            response: The JSON response
        """
        response = await call_next(request)

        return response

    @my_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        detail = exc.errors()
        body = exc.body
        logger.debug(f"error_422-statuscode: {status_code}\n")
        logger.debug(f"error_422-detail: {detail}\n")
        logger.debug(f"error_422-body: {body}\n")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    my_app.container = container
    my_app.include_router(chatbot_endpoints.chatbot)

    return my_app


app = create_app()
