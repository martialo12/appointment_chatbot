"""Containers module."""

from dependency_injector import containers, providers

from app.db.database import Database
from app.chatbot.repositories import GoogleCredentialsRepository
from app.chatbot.services import GoogleCredentialsService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(Database, db_url=config.db.sqlite.url)
    # db = providers.Singleton(Database, db_url=config.services.backend.environment.DATABASE_URL)
    # db = providers.Singleton(Database, db_url=config.db.postgresql.url)

    # chatbot
    gcreds_repository = providers.Factory(
        GoogleCredentialsRepository, session_factory=db.provided.session
    )

    gcreds_service = providers.Factory(
        GoogleCredentialsService, gcreds_repository=gcreds_repository
    )
