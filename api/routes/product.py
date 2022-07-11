import logging
from typing import Any, Dict, List
from uuid import UUID

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from tortoise.exceptions import DoesNotExist, IntegrityError, ValidationError
from tortoise.models import Model
from tortoise.queryset import QuerySet

from ..data import ProductAttributeModel, Repository
from ..data import use_repository, validate_data
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

@validate_data(attribute_model=ProductAttributeModel)
@use_repository(model=Product)
async def create_product(
        request: Request, 
        repository: Repository, 
        params: Dict[str, Any]
    ) -> JSONResponse:

    try:
        model: Model | Product = await repository.create(params=params)
        result: Dict[str, Any] = await repository.serialize_model(model=model)
    
    except (IntegrityError, ValidationError) as err:
        if isinstance(err, IntegrityError):
            err_args = getattr(err, "args")[0]
            detail = getattr(err_args, "args")[0] 
            raise HTTPException(status_code=422, detail=detail)

        err_args = getattr(err, "args")[0]
        raise HTTPException(status_code=422, detail=f"{err_args}")

    return JSONResponse(content=result, status_code=201)

@validate_data(attribute_model=ProductAttributeModel)
@use_repository(model=Product)
async def update_product(
    request: Request, 
    repository:Repository, 
    params: Dict[str, Any]
    ) -> Response:

    try:
        id: UUID = request.path_params["id"]
        model: Model | Product = await repository.update(id=id, params=params)
        result:  Dict[str, Any] = await repository.serialize_model(model=model)

    except DoesNotExist as err:
        logger.exception(err)
        raise HTTPException(status_code=404, detail=str(err))

    return JSONResponse(content=result, status_code=200)

routes = [
    Route(path="/", endpoint=get_products, methods=["GET"]),
    Route(path="/", endpoint=create_product, methods=["POST"]),
    Route(path="/{id:uuid}", endpoint=get_by_id, methods=["GET"]),
    Route(path="/{id:uuid}", endpoint=update_product, methods=["PATCH"])
]
