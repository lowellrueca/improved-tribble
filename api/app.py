""" Contains startup function for creating the application """

from starlette.applications import Starlette as App
from starlette.routing import Mount


def create_app():
    # imports
    from api.settings import DEBUG
    from api.routes import product_routes
    from api.events import on_startup, on_shutdown

    # routes
    routes = [
        Mount(path="/api/products/", routes=product_routes),
    ]

    # init app
    app: App = App(
        debug=DEBUG, routes=routes, 
        on_startup=[on_startup], 
        on_shutdown=[on_shutdown]
    )

    return app
