import logging
from uuid import UUID
from typing import Any, Dict, List, Type

from starlette.requests import Request
from tortoise.models import Model
from tortoise.queryset import QuerySet, QuerySetSingle

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

    async def update(self, id: int | UUID, params: dict) -> Model:
        model = await self._model.get(id=id)
        await model.update_from_dict(data=params)
        await model.save()
        return model

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
            return await f(repository=repository, *args, **kwargs)

        return fn
    return func_wrap
