import logging
import logging.config
from uvicorn import run

logging.config.fileConfig(fname="logging.conf")
logger = logging.getLogger("root")


def run_app():
    from api import create_app
    from api.settings import HOST, PORT

    app = create_app()
    run(app=app, host=HOST, port=PORT)


if __name__ == '__main__':
    try:
        logger.info("Starting web host")
        run_app()

    except Exception:
        logging.exception("An error occured while running the app")
