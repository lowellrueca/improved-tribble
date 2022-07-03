from decimal import Decimal
from pydantic import BaseModel, UUID4


class BaseResponseModel(BaseModel):
    id: UUID4 | int
    type_: str


class ProductResponse(BaseResponseModel):
    type_: str = "product"
    name: str
    price: Decimal

    class Config:
        orm_mode = True
