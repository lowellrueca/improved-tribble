from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DataModel:
    type: str
    attributes: Dict[str, Any]
