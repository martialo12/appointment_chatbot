"""Database module."""

from contextlib import asynccontextmanager, AbstractAsyncContextManager
from typing import Callable
import logging

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class Database:
    def __init__(self, db_url) -> None:
        self._engine = create_engine(url=db_url, echo=False)
        logger.debug(f"db url: {db_url}")
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractAsyncContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception as exc:
            logger.exception(f"Session rollback because of exception: {exc}")
            session.rollback()
            raise
        finally:
            session.close()
