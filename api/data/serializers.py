from typing import Any, Callable, Dict, List, cast

import orjson
from starlette.datastructures import URL
from tortoise.models import Model
from tortoise.queryset import QuerySet, QuerySetSingle

from .encoder import model_encoder


set_url: Callable[[URL], str] = lambda url: f"{url.scheme}://{url.hostname}:{url.port}{url.path}"

get_table_attr: Callable[[Model], str] = lambda model: getattr(
    cast(Model, model).Meta, "table")

dump_model: Callable[[Model], Dict[str, Any]] = lambda model: orjson.loads(
    orjson.dumps(model, default=model_encoder))

to_json_model: Callable[[Model], Dict[str, Any]] = lambda model: {
    "type": get_table_attr(model=model), **dump_model(model=model)}


class QuerySerializer:
    @staticmethod
    async def serialize_query_set(
        query_set:QuerySet, 
        url: URL
    ) -> List[Dict[str, Any]]:

        set_link: Callable[[Model], str] = lambda m: f"{set_url(url)}{getattr(m, 'id')}"
        models: List[Model] = await query_set
        result: List[Dict[str, Any]] = [{
                **to_json_model(model),
                "link": {"self": set_link(model)}}
            for model in models]

        return result

    @staticmethod
    async def serialize_query_set_single(
        query_set_single: QuerySetSingle,
        url: URL
    ) -> Dict[str, Any]:

        model: Model = await query_set_single
        result: Dict[str, Any] = {
            **to_json_model(model), 
            "link":{"self": set_url(url)}}

        return result
