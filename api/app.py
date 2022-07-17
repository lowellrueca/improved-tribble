import logging
from typing import List

from starlette.applications import Starlette as App
from starlette.middleware import Middleware
from starlette.routing import Mount

logger: logging.Logger = logging.getLogger("root")


def create_app():
    # imports
    from .data import (
        ContextService, 
        ContextServiceMiddleware, 
        ProductRepository,
        ProductSchema
    )
    from .settings import DEBUG
    from .routes import product_routes
    from .events import on_startup, on_shutdown

    contexts: List[ContextService] = [
        ContextService("product", ProductRepository, ProductSchema)
    ]

    # middlewares
    middlewares: List[Middleware] = [
        Middleware(ContextServiceMiddleware, contexts=contexts)
    ]

    # routes
    routes = [
        Mount(path="/api/products", routes=product_routes),
    ]

    # init app
    return App(
        debug=DEBUG, routes=routes, 
        middleware=middlewares,
        on_startup=[on_startup], 
        on_shutdown=[on_shutdown]
    )
