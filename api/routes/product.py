import logging

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from tortoise.queryset import QuerySet

from api.data import ProductResponse, serialize_query_set
from api.data.repository import Repository, use_repository
from api.data.schematics import serialize_query_single
from api.db import Product

logger = logging.getLogger("root")


@use_repository(model=Product)
async def get_products(request: Request, repository:Repository) -> JSONResponse:
    query_set: QuerySet[Product] = await repository.all()
    content = await serialize_query_set(request=request, query_set=query_set, response_model=ProductResponse) 
    return JSONResponse(content=content)

@use_repository(model=Product)
async def get_by_id(request: Request, repository:Repository) -> JSONResponse:
    query_set_single = await repository.get(param=request.path_params)
    content = await serialize_query_single(request=request, query_set_single=query_set_single, response_model=ProductResponse) 
    return JSONResponse(content=content)


routes = [
    Route(path="/", endpoint=get_products, methods=["GET"]),
    Route(path="/{id:uuid}", endpoint=get_by_id, methods=["GET"])
]
