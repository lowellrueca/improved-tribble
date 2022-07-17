import logging
from typing import List, NamedTuple, Optional, Type, cast

from marshmallow.exceptions import ValidationError
from marshmallow_jsonapi import Schema
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

            # for validating payload
            try:
                if request.method == "POST" or request.method == "PATCH":
                    payload = await request.json()
                    schema().load(payload)
                    data = payload["data"]["attributes"]
                    
                    # return function
                    return await f(repository=repo(), schema=schema, data=data, 
                        *args, **kwargs)

            # handle exception for payload errors
            except Exception as exc:
                if isinstance(exc, KeyError):
                    detail = f"Invalid input. expected key {exc}"
                    logger.exception(msg=detail)
                    raise HTTPException(status_code=422, detail=detail)

                if isinstance(exc, ValidationError):
                    if arg_schema := exc.args[0].get("_schema"):
                        detail = arg_schema[0]["detail"]
                        logger.exception(msg=detail)
                        raise HTTPException(status_code=422, detail=detail)
    
                    detail = f"An exception occured: {exc.args[0]}"
                    logger.debug(type(detail))
                    raise HTTPException(status_code=422, detail=detail)

                detail = f"An exception occured: {exc}"
                logger.exception(msg=detail)
                raise HTTPException(status_code=422, detail=detail)

            # return function
            return await f(repository=repo(), schema=schema, *args, **kwargs)

        return fn
    return func_wrap
