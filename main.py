import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.v1.router import api_router
from config import settings
from core.redis import redis_client
from core.database import engine
from models.user import Base

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await redis_client.ping()
        logging.info("✅ Подключено к Redis")
    except Exception as e:
        logging.error(f"❌ Не удалось подключиться к Redis: {e}")
        raise

    if settings.APP_ENV == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("✅ Таблицы созданы в PostgreSQL")

    yield
    await redis_client.close()
    logging.info("🔌 Redis соединение закрыто")

app = FastAPI(
    title="My FastAPI App",
    version="0.1.0",
    debug=settings.APP_ENV == "development",
    lifespan=lifespan
)

# Подключаем роуты
app.include_router(api_router, prefix="/api/v1")

