import logging
from typing import Any, Dict, List, Optional, Type
from uuid import UUID

from marshmallow_jsonapi.schema import Schema
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from tortoise.exceptions import DoesNotExist, ValidationError
from tortoise.models import Model

from ..data import RepositoryProtocol, context

logger = logging.getLogger("root")


@context(name="product")
async def get_products(
        request: Request, 
        repository: RepositoryProtocol,
        schema: Type[Schema]
    ) -> JSONResponse:

    global content
    try:
        models: List[Type[Model]] = await repository.all()
        content = schema().dump(obj=models, many=True)
    
    except Exception as exc:
        logger.exception(exc.args)
        raise HTTPException(status_code=500, detail=f"An unexpected error occured. {exc}")

    return JSONResponse(content=content)

@context(name="product")
async def get_product_by_id(
        request: Request, 
        repository: RepositoryProtocol,
        schema: Type[Schema]
    ) -> JSONResponse:

    global content
    try:
        model: Type[Model] = await repository.get(params=request.path_params)
        content = schema().dump(model)

    except DoesNotExist as exc:
        logger.exception(msg=str(exc))
        raise HTTPException(status_code=404, detail="Product does not exist")

    return JSONResponse(content=content)

@context(name="product")
async def create_product(
        request: Request, 
        repository: RepositoryProtocol,
        schema: Type[Schema],
        data: Dict[str, Any]
    ) -> JSONResponse:

    global content
    try:
        model: Type[Model] = await repository.create(params=data)
        content = schema().dump(obj=model)
    
    except ValidationError as exc:
        logger.exception(msg=exc)
        raise HTTPException(status_code=400, detail=f"An unexpected exception occured. '{exc}'")

    return JSONResponse(content=content)

@context(name="product")
async def update_product(
    request: Request, 
    repository: RepositoryProtocol,
    schema: Type[Schema],
    data: Dict[str, Any]
    ) -> Response:

    global content
    try:
        id: UUID = request.path_params["id"]
        model: Type[Model] = await repository.update(id=id, params=data)
        content = schema().dump(obj=model)

    except Exception as exc:
        logger.exception(exc.args)

    return JSONResponse(content=content)

@context(name="product")
async def delete_product(
        request: Request, 
        repository: RepositoryProtocol,
        schema: Optional[Type[Schema]]
    ) -> Response:

    try:
        logger.debug(msg="debugging delete_product endpoint")
        id: UUID = request.path_params["id"]
        await repository.delete(id=id)
    
    except Exception as exc:
        if isinstance(exc, DoesNotExist):
            logger.exception(msg=str(exc))
            raise HTTPException(status_code=404, detail="Product does not exist")

        logger.exception(str(exc.args))

    return Response(status_code=204)


routes = [
    Route(path="/", endpoint=get_products, methods=["GET"]),
    Route(path="/", endpoint=create_product, methods=["POST"]),
    Route(path="/{id:uuid}", endpoint=get_product_by_id, methods=["GET"]),
    Route(path="/{id:uuid}", endpoint=update_product, methods=["PATCH"]),
    Route(path="/{id:uuid}", endpoint=delete_product, methods=["DELETE"])
]
