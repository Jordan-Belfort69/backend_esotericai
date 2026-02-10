# app/db/postgres.py

import os
import asyncio
import re
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

# заменяем префикс для async-движка
ASYNC_DB_URL = re.sub(r"^postgresql:", "postgresql+psycopg:", DATABASE_URL)


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# фикс event loop для Windows (как в test_neon.py)
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
