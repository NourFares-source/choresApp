# tests/test_worker.py
import pytest
from app.worker import send_welcome_email, daily_chore_reminder
import os
@pytest.mark.asyncio
async def test_send_welcome_email_task():
    """Unit test the worker function directly without needing Redis running."""
    # Arq functions expect a context dictionary as the first argument (ctx)
    ctx = {} 
    
    result = await send_welcome_email(ctx, email="test@example.com", username="testuser")
    
    assert result["status"] == "sent"
    assert result["recipient"] == "test@example.com"

@pytest.mark.asyncio
async def test_daily_chore_reminder_task():
    """Unit test the scheduled task function."""
    ctx = {}
    
    # Ensures the cron function executes to completion without throwing exceptions
    await daily_chore_reminder(ctx)