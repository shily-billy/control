"""Event Bus - Handles communication between agents"""

from typing import Callable, Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from loguru import logger
import asyncio


class EventType(Enum):
    """Event types in the system"""
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_ERROR = "agent_error"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MESSAGE_RECEIVED = "message_received"
    PRODUCT_POSTED = "product_posted"
    PRODUCT_UPDATED = "product_updated"
    PRODUCT_DELETED = "product_deleted"
    SALE_RECORDED = "sale_recorded"
    INVENTORY_UPDATED = "inventory_updated"
    CUSTOM = "custom"


class Event:
    """Event object"""

    def __init__(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        priority: int = 5
    ):
        """
        Initialize event

        Args:
            event_type: Type of event
            source: Agent that triggered the event
            data: Event data
            priority: Event priority (1-10, higher = more important)
        """
        self.event_type = event_type
        self.source = source
        self.data = data
        self.priority = priority
        self.timestamp = datetime.now()
        self.event_id = f"{source}_{event_type.value}_{datetime.now().timestamp()}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary

        Returns:
            Dict: Event as dictionary
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "data": self.data,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat()
        }


class EventBus:
    """Event bus for pub/sub communication between agents"""

    def __init__(self):
        """
        Initialize event bus
        """
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history_size = 10000

    def subscribe(self, event_type: EventType, callback: Callable) -> str:
        """
        Subscribe to an event type

        Args:
            event_type: Type of event to subscribe to
            callback: Callback function to execute when event occurs

        Returns:
            str: Subscription ID
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        subscription_id = f"{event_type.value}_{len(self.subscribers[event_type])}"
        logger.info(f"Subscription created: {subscription_id}")
        return subscription_id

    def unsubscribe(self, event_type: EventType, callback: Callable) -> bool:
        """
        Unsubscribe from an event type

        Args:
            event_type: Type of event
            callback: Callback function to remove

        Returns:
            bool: True if unsubscribed successfully
        """
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                logger.info(f"Unsubscribed from {event_type.value}")
                return True
            except ValueError:
                logger.warning(f"Callback not found for {event_type.value}")
                return False
        return False

    async def publish(self, event: Event):
        """
        Publish an event

        Args:
            event: Event to publish
        """
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)

        logger.info(f"Event published: {event.event_id} (type: {event.event_type.value})")

        # Call all subscribers
        if event.event_type in self.subscribers:
            tasks = []
            for callback in self.subscribers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        tasks.append(callback(event))
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Error in callback for {event.event_type.value}: {e}")

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get event history

        Args:
            event_type: Filter by event type (None for all)
            limit: Maximum number of events to return

        Returns:
            List: Event history
        """
        history = self.event_history
        if event_type:
            history = [e for e in history if e.event_type == event_type]

        return [e.to_dict() for e in history[-limit:]]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get event bus statistics

        Returns:
            Dict: Statistics
        """
        event_counts = {}
        for event in self.event_history:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            "total_events": len(self.event_history),
            "total_subscribers": sum(len(v) for v in self.subscribers.values()),
            "event_counts": event_counts,
            "subscriptions": {k.value: len(v) for k, v in self.subscribers.items()}
        }
