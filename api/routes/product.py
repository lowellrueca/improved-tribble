import logging
from typing import Any, Dict, List

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException
from tortoise.queryset import QuerySet
from tortoise.exceptions import DoesNotExist

from ..data import Repository, use_repository
from ..db import Product

logger = logging.getLogger("root")


@use_repository(model=Product)
async def get_products(
        request: Request, 
        repository:Repository
    ) -> JSONResponse:

    content = List[Dict[str, Any]]
    try:
        query_set: QuerySet[Product] = await repository.all()
        content = await repository.serialize_query_set(query_set=query_set)
    
    except Exception as err:
        logger.exception(err)

    return JSONResponse(content=content)

@use_repository(model=Product)
async def get_by_id(
        request: Request, 
        repository:Repository
    ) -> JSONResponse:

    try:
        query_set_single = await repository.get(param=request.path_params)
        content = await repository.serialize_query_set_single(
            query_set_single=query_set_single) 

    except (Exception, DoesNotExist) as err:
        logger.exception(err)
        raise HTTPException(status_code=404, detail="Product does not exist")

    return JSONResponse(content=content)


routes = [
    Route(path="/", endpoint=get_products, methods=["GET"]),
    Route(path="/{id:uuid}", endpoint=get_by_id, methods=["GET"])
]
