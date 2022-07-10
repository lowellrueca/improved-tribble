import logging
from typing import Any, Dict, List, Type

from starlette.requests import Request
from starlette.exceptions import HTTPException
from tortoise.models import Model
from tortoise.queryset import QuerySet, QuerySetSingle

from .models import DataModel
from .serializers import QuerySerializer

logger: logging.Logger = logging.getLogger("root")


class Repository:
    serializer: Type[QuerySerializer] = QuerySerializer

    def __init__(self, model: Type[Model], request: Request):
        self._model = model
        self._request = request
        self._url = request.url

    async def all(self) -> QuerySet:
        return self._model.all()

    async def get(self, param:dict) -> QuerySetSingle:
        return self._model.get(**param)

    async def create(self, params: dict) -> Model:
        return await self._model.create(**params)

    async def serialize_query_set(
            self, 
            query_set: QuerySet
    ) -> List[Dict[str, Any]]:

        return await self.serializer.serialize_query_set(
            query_set=query_set, url=self._url)
        
    async def serialize_query_set_single(
        self, 
        query_set_single: QuerySetSingle
    ) -> Dict[str, Any]:

        return await self.serializer.serialize_query_set_single(
            query_set_single=query_set_single, url=self._url)

    async def serialize_model(self, model: Model) -> Dict[str, Any]:
        return await self.serializer.serialize_model(
            model=model, url=self._url)


def use_repository(model:Type[Model]):
    def func_wrap(f):
        async def fn(*args, **kwargs):
            request = args[0]
            repository = Repository(model=model, request=request)

            # validate data model against the orm model table
            # on post or patch method
            if request.method == "POST" or request.method == "PATCH":
                model_table: str = getattr(model.Meta, "table")
                data_model: DataModel = request.state.data_model            

                try:
                    assert model_table == data_model.type
                    return await f(repository=repository, 
                        data_model=data_model, *args, **kwargs)

                except AssertionError as err:
                    logger.exception(err)
                    raise HTTPException(status_code=404, 
                        detail="Assertion error occured: type of {type} against type of {table}"
                        .format(type=data_model.type, table=model_table))

            return await f(repository=repository, *args, **kwargs)

        return fn
    return func_wrap
