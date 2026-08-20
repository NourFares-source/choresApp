import json
import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import redis.asyncio as aioredis

router = APIRouter(prefix="/analytics", tags=["Analytics & Caching"])

# Connect to Redis
redis_client = aioredis.from_url("redis://127.0.0.1:6379", decode_responses=True)


@router.get("/family-summary")
async def get_family_summary(db: Session = Depends(get_db)):
    cache_key = "analytics:family_summary"

    # Step 1: Check Redis (Cache Hit?)
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print("\n⚡ [CACHE HIT] Data fetched from Redis RAM (~2ms)!")
        return json.loads(cached_data)

    # Step 2: Cache Miss — Simulate heavy DB calculations
    print("\n🐢 [CACHE MISS] Querying PostgreSQL database (~3000ms)...")
    await asyncio.sleep(3)  # Simulates complex SQL joins & point calculations
    
    report_data = {
        "total_chores_completed": 158,
        "completion_rate": "94%",
        "top_child": "Alex",
        "total_allowance_earned": "$45.00"
    }

    # Step 3: Save to Redis with a 60-second TTL
    await redis_client.set(cache_key, json.dumps(report_data), ex=60)

    return report_data

#Let's add a clear route or update trigger to delete that cached key whenever database changes occur.
@router.post("/invalidate-summary")
async def invalidate_summary_cache():
    """Deletes the analytics summary key from Redis so the next GET fetches fresh DB data."""
    deleted_count = await redis_client.delete("analytics:summary")
    
    if deleted_count > 0:
        print("\n🗑️ [CACHE INVALIDATED] 'analytics:summary' key removed from Redis!")
        return {"message": "Cache invalidated successfully!"}
    
    return {"message": "No cache key found to invalidate."}


#Step 4.3: Automatic Response Caching with fastapi-cache2

##install fastapi-cache2 : pip install "fastapi-cache2[redis]"

#test

from fastapi_cache.decorator import cache

@router.get("/auto-cached-report")
@cache(expire=60)  # Caches the entire HTTP response in Redis for 60 seconds!
async def get_auto_cached_report():
    print("\n🐢 Running heavy calculation for 3 seconds...")
    await asyncio.sleep(3)
    return {"report_type": "Weekly Summary", "status": "Generated"}