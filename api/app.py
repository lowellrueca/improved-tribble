import logging
from starlette.applications import Starlette as App
from starlette.routing import Mount
from starlette.middleware import Middleware

logger: logging.Logger = logging.getLogger("root")


def create_app():
    # imports
    from .settings import DEBUG
    from .routes import product_routes
    from .events import on_startup, on_shutdown
    from .middlewares import RepositoriesMiddleware
    from .data import ProductRepository

    repositories = [ProductRepository]

    # middlewares
    middlewares = [
        Middleware(RepositoriesMiddleware, repositories=repositories)
    ]

    # routes
    routes = [
        Mount(path="/api/products", routes=product_routes),
    ]

    # init app
    app: App = App(
        debug=DEBUG, routes=routes, 
        middleware=middlewares,
        on_startup=[on_startup], 
        on_shutdown=[on_shutdown]
    )

    return app
