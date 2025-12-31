"""Event bus for agent communication"""
import asyncio
from typing import Dict, List, Callable
from collections import defaultdict
from core.logger import setup_logger

logger = setup_logger(__name__)

class EventBus:
    """Pub/Sub event bus for inter-agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.queue = asyncio.Queue()
        self.running = False
        self._task = None
        logger.info("EventBus initialized")
    
    async def start(self):
        """Start event processing"""
        self.running = True
        self._task = asyncio.create_task(self._process_events())
        logger.info("EventBus started")
    
    async def stop(self):
        """Stop event processing"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus stopped")
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")
    
    async def publish(self, event_type: str, data: dict):
        """Publish an event"""
        await self.queue.put((event_type, data))
        logger.debug(f"Event published: {event_type}")
    
    async def _process_events(self):
        """Process events from queue"""
        while self.running:
            try:
                event_type, data = await asyncio.wait_for(
                    self.queue.get(), timeout=1.0
                )
                
                # Call all subscribers
                for callback in self.subscribers.get(event_type, []):
                    try:
                        await callback(data)
                    except Exception as e:
                        logger.error(f"Error in event callback: {e}")
            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
