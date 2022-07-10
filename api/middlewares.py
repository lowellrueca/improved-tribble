import logging
from typing import List, Optional, Type

from starlette.middleware.base import (
        BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint)

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from tortoise.models import Model

from .data import DataModel

logger: logging.Logger = logging.getLogger("root")


class DataValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, models: List[Type[Model]], dispatch: Optional[DispatchFunction] = None) -> None:
        super().__init__(app, dispatch)
        self._models = models

    async def dispatch(
        self, request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:

        if request.method == "POST" or request.method == "PATCH":
            try:
                # retrieve the models table
                model_tables = tuple(map(
                    lambda m: getattr(m.Meta, "table"), self._models))

                # retrieve the payload
                json_data = await request.json()
                data = json_data["data"]

                # validate the type from payload against the model tables
                if not data["type"] in model_tables:
                    return Response(
                        content=f"Type of {data['type']} not in the database", 
                        status_code=400)

                request.state.data_model = DataModel(
                    type=data["type"], attributes=data["attributes"])

            except KeyError as err:
                logger.exception(err)
                return Response(content=f"KeyError: {err}", status_code=400)

        return await call_next(request)
