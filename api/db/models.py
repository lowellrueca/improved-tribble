""" Contains database models """

from tortoise.fields import CharField, UUIDField, DecimalField
from tortoise.models import Model


class AbstractModel(Model):
    id = UUIDField(pk=True)

    class Meta:
        abstract = True


class Product(AbstractModel):
    name = CharField(max_length=128, nullable=False)
    price = DecimalField(max_digits=8, decimal_places=2)

    class Meta: 
        table = "desktop"
