import logging
from typing import List
from uuid import UUID

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

from ..data import ProductRepository, ProductSchema
from ..data import use_repository
from ..db import Product

logger = logging.getLogger("root")


@use_repository(repository=ProductRepository)
async def get_products(
        request: Request, 
        repository: ProductRepository
    ) -> JSONResponse:

    global content
    try:
        models: List[Product] = await repository.all()
        content = ProductSchema().dump(obj=models, many=True)
    
    except Exception as err:
        logger.exception(err.args)

    return JSONResponse(content=content)

@use_repository(repository=ProductRepository)
async def get_product_by_id(
        request: Request, 
        repository: ProductRepository
    ) -> JSONResponse:

    global content
    try:
        model = await repository.get(params=request.path_params)
        content = ProductSchema().dump(obj=model)

    except Exception as err:
        if isinstance(err, DoesNotExist):
            raise HTTPException(status_code=404, detail="Product does not exist")

        logger.exception(err)

    return JSONResponse(content=content)

@use_repository(repository=ProductRepository)
async def create_product(
        request: Request, 
        repository: ProductRepository, 
    ) -> JSONResponse:

    try:
        payload = await request.json()
        schema: ProductSchema = ProductSchema()
        schema.load(payload)
        params = payload["data"]["attributes"]

        model: Model | Product = await repository.create(params=params)
        content = schema.dump(obj=model)
    
    except Exception as err:
        logger.exception(msg=err)
        raise HTTPException(status_code=422, detail=str(err))

    return JSONResponse(content=content, status_code=201)

@use_repository(repository=ProductRepository)
async def update_product(
    request: Request, 
    repository: ProductRepository, 
    ) -> Response:

    try:
        id: UUID = request.path_params["id"]
        payload = await request.json()
        schema = ProductSchema()
        schema.load(payload)
        params = payload["data"]["attributes"]

        model: Model | Product = await repository.update(id=id, params=params)
        content = schema.dump(obj=model)

    except Exception as err:
        if isinstance(err, DoesNotExist):
            raise HTTPException(status_code=404, detail="Product does not exists")
        logger.exception(err.args)
        raise HTTPException(status_code=404, detail=str(err.args))

    return JSONResponse(content=content, status_code=200)

@use_repository(repository=ProductRepository)
async def delete_product(request: Request, repository: ProductRepository) -> Response:
    try:
        id: UUID = request.path_params["id"]
        await repository.delete(id)
    
    except DoesNotExist as err:
        logger.exception(err)
        raise HTTPException(status_code=404, detail="Product does not exist")

    return Response(status_code=204)


routes = [
    Route(path="/", endpoint=get_products, methods=["GET"]),
    Route(path="/", endpoint=create_product, methods=["POST"]),
    Route(path="/{id:uuid}", endpoint=get_product_by_id, methods=["GET"]),
    Route(path="/{id:uuid}", endpoint=update_product, methods=["PATCH"]),
    Route(path="/{id:uuid}", endpoint=delete_product, methods=["DELETE"])
]
