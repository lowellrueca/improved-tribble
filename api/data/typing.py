from typing import TypeVar
from tortoise.models import Model

TModel = TypeVar("TModel", bound=Model)
