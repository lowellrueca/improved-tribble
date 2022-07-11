""" Contains startup function for creating the application """

from starlette.applications import Starlette as App
from starlette.routing import Mount
from starlette.middleware import Middleware


def create_app():
    # imports
    from .settings import DEBUG
    from .routes import product_routes
    from .events import on_startup, on_shutdown
    from .middlewares import DataValidationMiddleware
    from .db import __models__ as models

    # middlewares
    middlewares = [
        Middleware(DataValidationMiddleware, models=models)
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
