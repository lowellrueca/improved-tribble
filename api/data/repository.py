import logging
from typing import Generic, List, Type
from uuid import UUID

from starlette.requests import Request

from ..db import Product
from .typing import TModel

logger: logging.Logger = logging.getLogger("root")


class BaseRepository(Generic[TModel]):
    model: Type[TModel]

    async def all(self) -> List[TModel]:
        return await self.model.all()

    async def get(self, params:dict) -> TModel:
        return await self.model.get(**params)

    async def create(self, params: dict) -> TModel:
        return await self.model.create(**params)

    async def update(self, id: int | UUID, params: dict) -> TModel:
        if model := await self.model.get(id=id):
            await model.update_from_dict(data=params)
            await model.save()
        return model

    async def delete(self, id: int | UUID) -> None:
        if model := await self.model.get(id=id):
            await model.delete()
        return None


class ProductRepository(BaseRepository):
    model: Type[Product] = Product


def use_repository(repository: Type[BaseRepository]):
    def func_wrap(f):
        async def fn(*args, **kwargs):
            request: Request = args[0]
            repo: Type[BaseRepository] = tuple(filter(
                lambda x: x == repository, request.state.repositories))[0]
            return await f(repository=repo(), *args, **kwargs)

        return fn
    return func_wrap
