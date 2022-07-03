from tortoise import Tortoise


async def on_startup():
    from api.settings import DB_CONFIG
    from api.db import seed_data    

    await Tortoise.init(config=DB_CONFIG)
    await Tortoise.generate_schemas()
    await seed_data()

async def on_shutdown():
    await Tortoise.close_connections()
