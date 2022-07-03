from typing import Type
from tortoise.models import Model
from tortoise.queryset import QuerySet, QuerySetSingle


class Repository:
    def __init__(self, model: Type[Model]):
        self._model = model

    async def all(self) -> QuerySet:
        return self._model.all()

    async def get(self, param:dict) -> QuerySetSingle:
        return self._model.get(**param)


def use_repository(model:Type[Model]):
    def func_wrap(f):
        async def fn(*args, **kwargs):
            return await f(repository=Repository(model=model), *args, **kwargs)
        return fn
    return func_wrap
