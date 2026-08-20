# app/worker.py
import asyncio
from arq.connections import RedisSettings
from arq.cron import cron
import os
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


# --- Instant Task ---
async def send_welcome_email(ctx, email: str, username: str):
    print(f"\n[SPONGEBOB WORKER] Got order! Sending email to {email}...")
    await asyncio.sleep(5) 
    print(f"[SPONGEBOB WORKER] Finished! Welcome email sent to {username} ({email}).\n")
    return {"status": "sent", "recipient": email}


# --- Scheduled Task (Cron Job) ---
async def daily_chore_reminder(ctx):
    """Simulates sending a daily reminder to children with incomplete chores."""
    print("\n[CRON WORKER] ⏰ Running daily scheduled task: Checking incomplete chores...")
    # Here you would query PostgreSQL for incomplete chores and send notifications
    await asyncio.sleep(2)
    print("[CRON WORKER] ✅ Daily reminders sent successfully!\n")


async def notify_child_new_chore(ctx, child_email: str, chore_title: str):
    """Simulates notifying a child when a parent assigns them a new chore."""
    print(f"\n[WORKER] 🔔 Sending alert to {child_email}...")
    await asyncio.sleep(3)  # Simulate network notification delay
    print(f"[WORKER] ✅ Notification sent: 'Hey! You have a new chore: {chore_title}'\n")
    return {"status": "notified", "email": child_email}

# --- Worker Configuration ---
class WorkerSettings:
    # Functions triggered on-demand by FastAPI endpoints
    functions = [send_welcome_email,notify_child_new_chore]  
    
    # Scheduled tasks that run automatically on a timetable
    cron_jobs = [
        # Runs every minute for testing! (hour=8, minute=0 would run daily at 8:00 AM)
        cron(daily_chore_reminder, minute=set(range(0, 60)))
    ]
    
    redis_settings = RedisSettings.from_dsn(REDIS_URL)