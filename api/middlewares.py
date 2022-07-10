import logging

from starlette.middleware.base import (
        BaseHTTPMiddleware, RequestResponseEndpoint)

from starlette.requests import Request
from starlette.responses import Response

from .data import DataModel

logger: logging.Logger = logging.getLogger("root")


class DataValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:

        if request.method == "POST" or request.method == "PATCH":
            try:
                json_data = await request.json()
                data = json_data["data"]
                request.state.data_model = DataModel(
                        type=data["type"], attributes=data["attributes"])

            except KeyError as err:
                logger.exception(err)
                return Response(content=f"KeyError: {err}", status_code=404)

        return await call_next(request)
