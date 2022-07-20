import logging
from starlette.requests import Request
from starlette.routing import Route

logger = logging.getLogger("uvicorn.error")


async def schema(requests: Request):
    pass


routes = [Route(path="/", endpoint=schema, methods=["GET"], include_in_schema=False)]
