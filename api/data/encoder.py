import decimal
from typing import cast
from uuid import UUID

import orjson
from tortoise.models import Model


def model_encoder(obj):
    if isinstance(obj, bytes):
        return obj.decode(encoding="utf-8")

    if isinstance(obj, decimal.Decimal):
        return str(obj)

    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, Model):
        if id := getattr(obj, "id"):
            props = {k:v for k, v in obj.__dict__.items() 
                    if not cast(str, k).startswith("_") and k.find("id")}
            attrs = orjson.loads(orjson.dumps(props, default=lambda x: str(x)))
            return dict(id=id, attributes=attrs)

    raise TypeError
