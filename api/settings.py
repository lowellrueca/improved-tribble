from os import path
from starlette.config import Config


config = Config(env_file=path.abspath("envs/settings.env"))

DB_URL = config(key="DB_URL", cast=str, default="sqlite://:memory:")
DEBUG = config(key="DEBUG", cast=bool, default=True)
HOST = config(key="HOST", cast=str, default="0.0.0.0")
PORT = config(key="PORT", cast=int, default=8000)
