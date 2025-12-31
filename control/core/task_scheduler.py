"""Task Scheduler - Handles scheduling of agent tasks"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
import asyncio
import uuid
from dataclasses import dataclass


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ScheduleType(Enum):
    """Schedule type enumeration"""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class Task:
    """Task object"""
    task_id: str
    agent_name: str
    task_type: str
    data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    scheduled_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    priority: int = 5  # 1-10, higher = more important

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.scheduled_at is None:
            self.scheduled_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary

        Returns:
            Dict: Task as dictionary
        """
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "task_type": self.task_type,
            "status": self.status.value,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "result": self.result,
            "error": self.error,
            "priority": self.priority
        }


class TaskScheduler:
    """Task scheduler for managing agent tasks"""

    def __init__(self):
        """
        Initialize task scheduler
        """
        self.tasks: Dict[str, Task] = {}
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.is_running = False

    def create_task(
        self,
        agent_name: str,
        task_type: str,
        data: Dict[str, Any],
        priority: int = 5,
        scheduled_at: Optional[datetime] = None
    ) -> Task:
        """
        Create a new task

        Args:
            agent_name: Name of the agent to execute the task
            task_type: Type of task
            data: Task data
            priority: Task priority (1-10)
            scheduled_at: When to execute the task

        Returns:
            Task: Created task
        """
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            data=data,
            priority=priority,
            scheduled_at=scheduled_at or datetime.now()
        )
        self.tasks[task_id] = task
        logger.info(f"Task created: {task_id} for agent {agent_name}")
        return task

    def schedule_task(
        self,
        task_id: str,
        schedule_type: ScheduleType,
        interval: Optional[int] = None,
        next_run: Optional[datetime] = None
    ) -> bool:
        """
        Schedule a task for recurring execution

        Args:
            task_id: ID of the task
            schedule_type: Type of schedule
            interval: Interval in minutes (for custom schedules)
            next_run: Next execution time

        Returns:
            bool: True if scheduled successfully
        """
        try:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return False

            self.scheduled_tasks[task_id] = {
                "task_id": task_id,
                "schedule_type": schedule_type,
                "interval": interval,
                "next_run": next_run or datetime.now(),
                "created_at": datetime.now()
            }
            logger.info(f"Task {task_id} scheduled with {schedule_type.value} schedule")
            return True

        except Exception as e:
            logger.error(f"Failed to schedule task {task_id}: {e}")
            return False

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID

        Args:
            task_id: ID of the task

        Returns:
            Task: Task object or None if not found
        """
        return self.tasks.get(task_id)

    def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending tasks

        Returns:
            List: List of pending tasks
        """
        return [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]

    def get_tasks_for_agent(self, agent_name: str) -> List[Task]:
        """
        Get all tasks for an agent

        Args:
            agent_name: Name of the agent

        Returns:
            List: List of tasks
        """
        return [t for t in self.tasks.values() if t.agent_name == agent_name]

    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all scheduled tasks

        Returns:
            List: List of scheduled tasks
        """
        return list(self.scheduled_tasks.values())

    async def update_task_status(self, task_id: str, status: TaskStatus, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> bool:
        """
        Update task status

        Args:
            task_id: ID of the task
            status: New status
            result: Task result
            error: Error message if failed

        Returns:
            bool: True if updated successfully
        """
        try:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return False

            task = self.tasks[task_id]
            task.status = status
            task.result = result
            task.error = error

            if status == TaskStatus.RUNNING:
                task.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.completed_at = datetime.now()

            logger.info(f"Task {task_id} status updated to {status.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return False

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task

        Args:
            task_id: ID of the task

        Returns:
            bool: True if cancelled successfully
        """
        try:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return False

            task = self.tasks[task_id]
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.status = TaskStatus.CANCELLED
                logger.info(f"Task {task_id} cancelled")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False

    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get scheduler status

        Returns:
            Dict: Scheduler status
        """
        statuses = {
            TaskStatus.PENDING.value: 0,
            TaskStatus.RUNNING.value: 0,
            TaskStatus.COMPLETED.value: 0,
            TaskStatus.FAILED.value: 0,
            TaskStatus.CANCELLED.value: 0,
            TaskStatus.PAUSED.value: 0
        }

        for task in self.tasks.values():
            statuses[task.status.value] += 1

        return {
            "total_tasks": len(self.tasks),
            "scheduled_tasks": len(self.scheduled_tasks),
            "is_running": self.is_running,
            "task_statuses": statuses
        }
