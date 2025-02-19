from decouple import config
from sqlalchemy import create_engine

PG_HOST = config('PG_HOST')
PG_PORT = config('PG_PORT')
PG_DATABASE = config('PG_DATABASE')
PG_USER = config('PG_USER')
PG_PASSWORD = config('PG_PASSWORD')

engine = create_engine(
    f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}',
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)
