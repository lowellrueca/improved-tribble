import logging
from typing import Any, Dict, Generic, List, Protocol, Type, TypeVar
from uuid import UUID

from tortoise.models import Model

from ..db import Product

logger: logging.Logger = logging.getLogger("uvicorn.error")


T = TypeVar("T")
TModel = TypeVar("TModel", bound=Model)


class RepositoryProtocol(Protocol[T]):
    async def all(self) -> List[T]:
        ...

    async def get(self, params:dict) -> T:
        ...

    async def create(self, params: dict) -> T:
        ...

    async def update(self, id: int | UUID, params: Dict[str, Any]) -> T:
        ...

    async def delete(self, id: int | UUID) -> None:
        ...


class BaseRepository(Generic[TModel]):
    model: Type[TModel]

    async def all(self) -> List[TModel]:
        return await self.model.all()

    async def get(self, params:dict) -> TModel:
        return await self.model.get(**params)

    async def create(self, params: dict) -> TModel:
        return await self.model.create(**params)

    async def update(self, id: int | UUID, params: Dict[str, Any]) -> TModel:
        if model := await self.model.get(id=id):
            await model.update_from_dict(data=params)
            await model.save()
        return model

    async def delete(self, id: int | UUID) -> None:
        if model := await self.model.get(id=id):
            await model.delete()
        return None


class ProductRepository(BaseRepository):
    model: Type[Model] = Product
