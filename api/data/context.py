import logging
from typing import List, NamedTuple, Optional, Type, cast

from marshmallow.exceptions import ValidationError
from marshmallow_jsonapi import Schema
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from starlette.exceptions import HTTPException
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from .repository import BaseRepository

logger: logging.Logger = logging.getLogger("root")

class ContextService(NamedTuple):
    name: str
    repository: Type[BaseRepository]
    schema: Type[Schema]


class ContextServiceMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: ASGIApp, 
        contexts: List[ContextService], 
        dispatch: Optional[DispatchFunction] = None
    ) -> None:

        super().__init__(app=app, dispatch=dispatch)
        self._contexts = contexts

    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:

        try:
            request.state.contexts = self._contexts
            
        except Exception as exc:
            logger.exception(str(exc))

        return await call_next(request)


def context(name:str):
    def func_wrap(f):
        async def fn(*args, **kwargs):
            request: Request = args[0]

            context: ContextService = tuple(filter(lambda x: 
                cast(ContextService, x).name == name, 
                request.state.contexts))[0]

            repo: Type[BaseRepository] = context.repository
            schema: Type[Schema] = context.schema

            # to validate payload on post or on patch endpoints
            try:
                if request.method == "POST" or request.method == "PATCH":
                    payload = await request.json()
                    schema().load(payload)
                    data = payload["data"]["attributes"]

                    return await f(repository=repo(), schema=schema, data=data, 
                        *args, **kwargs)

            # to handle exceptions occured for the payload errors
            except ValidationError as exc:
                if exc_schema := exc.args[0].get("_schema"):
                    detail = exc_schema[0].get("detail")
                    logger.exception(msg=detail)
                    raise HTTPException(status_code=400, detail=detail)

                logger.exception(msg=f"An exception occured. {exc}")
                raise HTTPException(status_code=400, detail=str(exc))

            except IncorrectTypeError as exc:
                detail = f"An exception occured {exc}"
                logger.exception(msg=detail)
                raise HTTPException(status_code=400, detail=detail)
            
            except KeyError as exc:
                detail = f"Invalid input. Expected key {exc}"
                logger.exception(msg=detail)
                raise HTTPException(status_code=400, detail=detail)

            return await f(
                repository=repo(), schema=schema, *args, **kwargs
            )

        return fn
    return func_wrap
