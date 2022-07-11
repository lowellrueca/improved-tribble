from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict


@dataclass
class ProductAttributeModel:
    name: str = field(default_factory=str, init=True)
    price: Decimal = field(default_factory=Decimal, init=True)


@dataclass
class DataModel:
    type: str
    attributes: Dict[str, Any]
