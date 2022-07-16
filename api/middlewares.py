import logging
from typing import List, Optional, Type

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from .data import BaseRepository

logger: logging.Logger = logging.getLogger("root")


class RepositoriesMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: ASGIApp, 
        repositories: List[Type[BaseRepository]], 
        dispatch: Optional[DispatchFunction] = None
    ) -> None:

        super().__init__(app=app, dispatch=dispatch)
        self._repositories = tuple(repositories)

    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:

        try:
            request.state.repositories = self._repositories
            
        except Exception as err:
            logger.exception(str(err))

        return await call_next(request)
