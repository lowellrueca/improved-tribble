import decimal
import orjson
from starlette.requests import Request


def create_link(request: Request, id:str | None = None) -> str:
    url_scheme = request.url.scheme
    url_hostname = request.url.hostname
    url_port = request.url.port
    url_path = request.url.path
    url = f"{url_scheme}://{url_hostname}:{url_port}{url_path}"
    if id:
        return f"{url}{id}"
    return url

def default(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    
    if isinstance(obj, bytes):
        return obj.decode(encoding="utf-8")
    raise TypeError

process_data_response = lambda data_resp, req, mod, lnk: data_resp(
        type = mod.type_,
        id = f"{mod.id}",
        attributes= serialize_attrs(mod),
        link=lnk(self=create_link(request=req, id=f"{mod.id}"))
    ) 

serialize_attrs = lambda x: orjson.loads(
        orjson.dumps(x.dict(exclude={"id", "type_"}), default=default)
    )
