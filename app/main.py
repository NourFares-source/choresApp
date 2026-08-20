from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.routes import auth_routes , chores_routes , analytics

from arq import create_pool
from arq.connections import RedisSettings

## automatic redis caching with fastapi-cache2
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
import os
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis cache backend on server startup
    # redis = aioredis.from_url("redis://127.0.0.1:6379")
    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # yield
    #docker 
    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield



# Create tables in the database automatically if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)
app.include_router(auth_routes.router)
app.include_router(chores_routes.router)
app.include_router(analytics.router)
@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}


@app.post("/test-background-job", status_code=201)
async def trigger_job(email: str, username: str):
    """Hand the ticket to Squidward (Redis) and respond to the user immediately."""
    
    # 1. Connect to Redis queue
    redis_pool = await create_pool(RedisSettings(host="127.0.0.1", port=6379))
    
    # 2. Push job to the queue
    await redis_pool.enqueue_job("send_welcome_email", email, username)
    
    # 3. Return instantly (~20ms)
    return {
        "message": "User registered successfully!",
        "background_job": "Queued in Redis"
    }
    
