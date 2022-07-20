import logging
import logging.config
from uvicorn import run

logger = logging.getLogger("uvicorn.error")


def run_app():
    from api import create_app
    from api.settings import HOST, PORT

    app = create_app()
    run(app=app, host=HOST, port=PORT)


if __name__ == '__main__':
    try:
        run_app()

    except Exception:
        logger.exception("An error occured while running the app")
