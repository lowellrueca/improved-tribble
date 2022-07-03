""" Contains classes and methods for creating structured schemas """

from typing import Any, List, Type, TypedDict

from starlette.requests import Request
from tortoise.queryset import QuerySet, QuerySetSingle

from .models import BaseResponseModel
from .helpers import create_link, process_data_response


class Link(TypedDict, total=True):
    self: str


class DataResponse(TypedDict, total=True):
    type: str
    id: str
    attributes: Any
    link: Link


class Meta(TypedDict, total=True):
    link: Link


async def serialize_query_set(
        request: Request, 
        query_set: QuerySet, 
        response_model: Type[BaseResponseModel]
    ) -> dict:

    # map to a pydantic model for serialization
    models = map(lambda m: response_model.from_orm(m), await query_set)
    data: List[DataResponse] = [
            process_data_response(
                data_resp=DataResponse, req=request, mod=m, lnk=Link
            ) 
            for m in list(models)
        ]

    meta: Meta = Meta(link=Link(self=create_link(request=request)))
    return {"data": data, "meta": meta}

async def serialize_query_single(
        request: Request, 
        query_set_single: QuerySetSingle, 
        response_model: Type[BaseResponseModel]
    ) -> dict:
    model = response_model.from_orm(await query_set_single)
    data: DataResponse = process_data_response(
            data_resp=DataResponse, req=request, mod=model, lnk=Link
        )
    return {"data": data}
