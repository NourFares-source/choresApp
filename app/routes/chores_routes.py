from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session 
from typing import List, Optional
from datetime import datetime, date, timedelta
from arq import create_pool
from arq.connections import RedisSettings
from app.schemas import TaskCreate, TaskResponse , ReportResponse
from app.models import Task, Parent, Child
from app.database import get_db 
from app.auth import get_current_parent, get_current_child  # 💡 Role-specific dependencies

router = APIRouter(prefix="/chores", tags=["Chores"])


# ==========================================
# PARENT ROUTES
# ==========================================

@router.post("/addChore", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def addChore(
    data: TaskCreate, 
    db: Session = Depends(get_db), 
    current_parent: Parent = Depends(get_current_parent) # 🔒 Only Parents allowed!
):
    # 1. Verify child exists and belongs to this parent
    child = db.query(Child).filter(
        Child.username == data.childUsername,
        Child.parent_id == current_parent.id  # 💡 Ensure parent owns this child record
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Child '{data.childUsername}' not found under your account"
        )
        
    # 2. Calculate due time using timer (hours)
    due_time = datetime.utcnow() + timedelta(hours=data.timer)

    # 3. Create task
    new_chore = Task(
        title=data.title,
        description=data.description,
        due_time=due_time,
        child_id=child.id
    )
    db.add(new_chore)
    db.commit()
    db.refresh(new_chore)
    redis_pool = await create_pool(RedisSettings(host="127.0.0.1", port=6379))
    await redis_pool.enqueue_job("notify_child_new_chore", child.email, new_chore.title)

    # 3. Respond immediately to Parent
    # return {
    #     "message": "Chore created and assigned successfully!",
    #     "chore_title": new_chore.title
    # }
    return new_chore


@router.delete("/removeChore/{chore_id}", status_code=status.HTTP_204_NO_CONTENT)
def deleteChore(
    chore_id: int, 
    db: Session = Depends(get_db), 
    current_parent: Parent = Depends(get_current_parent) # 🔒 Only Parents allowed!
):
    chore = db.query(Task).filter(Task.id == chore_id).first()
    if not chore: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    db.delete(chore)
    db.commit()
    return None  # HTTP 204 should return no content body!


@router.get("/getChildChores/{child_username}", response_model=List[TaskResponse])
def getChores(
    child_username: str, 
    target_date: Optional[date] = Query(None, description="Filter chores by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db), 
    current_parent: Parent = Depends(get_current_parent) # 🔒 Only Parents allowed!
):
    # 1. Fetch child verified against parent
    child = db.query(Child).filter(
        Child.childUsername == child_username,
        Child.parent_id == current_parent.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Child '{child_username}' not found under your account"
        )

    # 2. Build base query
    query = db.query(Task).filter(Task.child_id == child.id)

    # 3. Filter by date range (from 00:00:00 to 23:59:59 on the target date)
    if target_date:
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        query = query.filter(Task.created_at >= start_of_day, Task.created_at <= end_of_day)

    return query.all()


# ==========================================
# CHILD ROUTES
# ==========================================

@router.patch("/{chore_id}/complete", response_model=TaskResponse)
def completeChore(
    chore_id: int, 
    db: Session = Depends(get_db), 
    current_child: Child = Depends(get_current_child) # 🔒 Only Children allowed!
):
    # Fetch chore assigned strictly to THIS child
    chore = db.query(Task).filter(
        Task.id == chore_id, 
        Task.child_id == current_child.id
    ).first()

    if not chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Chore not found or not assigned to you"
        )

    chore.status = "completed"
    db.commit()
    db.refresh(chore)
    return chore


@router.get("/my-chores", response_model=List[TaskResponse])
def get_your_chores(
    target_date: Optional[date] = Query(None, description="Filter chores by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_child: Child = Depends(get_current_child) # 👈 Dependency returns logged-in Child object
):
    query = db.query(Task).filter(Task.child_id == current_child.id) # 👈 Uses current_child.id!
    
    if target_date:
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        query = query.filter(Task.created_at >= start_of_day, Task.created_at <= end_of_day)

    return query.all()




@router.get("/getReport/{child_username}", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def getReport(
    child_username: str, 
    db: Session = Depends(get_db), 
    current_parent: Parent = Depends(get_current_parent) # ✅ Fixed Depends syntax
):
    # 1. Fetch child and verify they belong to current_parent
    child = db.query(Child).filter(
        Child.childUsername == child_username,  # ✅ Attribute name matches Child model
        Child.parent_id == current_parent.id    # 🔒 Ownership check
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Child '{child_username}' not found under your account"
        )

    # 2. Fetch all tasks for this child directly from DB
    chores = db.query(Task).filter(Task.child_id == child.id).all()
    
    total = len(chores)
    completed = 0
    uncompleted = 0

    for ch in chores:
        if ch.status == "completed":
            completed += 1 # ✅ Python syntax for increment
        else:
            uncompleted += 1

    # 3. Calculate percentage safely (avoiding ZeroDivisionError)
    if total > 0:
        perComp = (completed / total) * 100.0
    else:
        perComp = 0.0 # Default to 0.0 if no chores assigned yet

    # 4. Save report record to DB
    new_report = Report(
        child_id=int(child.id), 
        evaluation=perComp
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report