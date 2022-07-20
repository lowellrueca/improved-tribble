import logging
from tortoise import Tortoise
from tortoise.exceptions import OperationalError
from starlette.exceptions import HTTPException

logger: logging.Logger = logging.getLogger("uvicorn.error")

async def on_startup():
    from .settings import DB_URL
    from .db import seed_data    

    try:
        logger.info("Initializing DB")
        await Tortoise.init(db_url=DB_URL, modules={"models": ["api.db"]})
        await Tortoise.generate_schemas()
        await seed_data()
    
    except OperationalError as exc:
        logger.exception(f"An exception occured: {exc}")
        raise HTTPException(status_code=500, detail="An internal server error occured")

async def on_shutdown():
    await Tortoise.close_connections()
