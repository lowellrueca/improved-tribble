from marshmallow_jsonapi import Schema, fields


class ProductSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str()
    price = fields.Decimal(as_string=True)
    metadata = fields.DocumentMeta()

    class Meta:
        type_ = "product"
        self_url = "/product/{id}"
        self_url_kwargs = {"id": "<id>"}
        self_url_many = "/product"
