"""Pydantic schemas for the tasks API."""
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, description="Task title (required)")


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    done: bool | None = None


class Task(BaseModel):
    id: int
    title: str
    done: bool
