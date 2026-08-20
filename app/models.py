from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base




class Parent(Base):
    __tablename__ = 'parents'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    fullName = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    username = Column(String , unique = True , index=True)

    # Relationship: One Parent has Multiple Children
    children = relationship("Child", back_populates="parent")


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String , unique = True , index=True)

    fullName = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign Key pointing to parents.id
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)

    # Relationships
    parent = relationship("Parent", back_populates="children")
    tasks = relationship("Task", back_populates="child")
    reports = relationship("Report", back_populates="child")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="No description required")
    due_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="uncompleted", nullable=False)

    # Foreign Key pointing to children.id
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)

    # Relationship back to Child
    child = relationship("Child", back_populates="tasks")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key pointing to children.id (Fixed from users.id)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    # Wrapped with Column() (Fixed syntax)
    evaluation = Column(Float, nullable=False)
    notes = Column(String, default="no current notes")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to Child
    child = relationship("Child", back_populates="reports")
    

