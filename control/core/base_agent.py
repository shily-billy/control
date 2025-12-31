"""Base Agent Class - Parent class for all agents"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import asyncio
import json
from loguru import logger


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    OFFLINE = "offline"


class AgentType(Enum):
    """Agent type enumeration"""
    MARKETPLACE = "marketplace"
    SOCIAL = "social"
    MESSAGING = "messaging"
    AFFILIATE = "affiliate"


class BaseAgent(ABC):
    """Base class for all agents in the control system"""

    def __init__(
        self,
        name: str,
        agent_type: AgentType,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base agent

        Args:
            name: Agent name (e.g., 'DivarAgent')
            agent_type: Type of agent (marketplace, social, messaging, affiliate)
            credentials: Login credentials for the platform
            config: Configuration settings for the agent
        """
        self.name = name
        self.agent_type = agent_type
        self.credentials = credentials or {}
        self.config = config or {}
        self.status = AgentStatus.OFFLINE
        self.created_at = datetime.now()
        self.last_activity = None
        self.error_log: List[Dict[str, Any]] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.is_authenticated = False

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the platform

        Returns:
            bool: True if authentication successful
        """
        pass

    @abstractmethod
    async def start(self):
        """
        Start the agent
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        Stop the agent
        """
        pass

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task

        Args:
            task: Task to process

        Returns:
            Dict: Result of task processing
        """
        pass

    async def queue_task(self, task: Dict[str, Any]):
        """
        Add a task to the agent's queue

        Args:
            task: Task to queue
        """
        await self.task_queue.put(task)
        logger.info(f"Task queued in {self.name}: {task.get('task_id')}")

    async def get_status(self) -> Dict[str, Any]:
        """
        Get agent status

        Returns:
            Dict: Agent status information
        """
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "authenticated": self.is_authenticated,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "pending_tasks": self.task_queue.qsize(),
            "error_count": len(self.error_log)
        }

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log an error

        Args:
            error: The exception that occurred
            context: Additional context information
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        self.error_log.append(error_entry)
        logger.error(f"Error in {self.name}: {error}", extra={"context": context})

    def update_activity(self):
        """
        Update last activity timestamp
        """
        self.last_activity = datetime.now()

    async def health_check(self) -> bool:
        """
        Perform health check

        Returns:
            bool: True if agent is healthy
        """
        try:
            if self.status == AgentStatus.ERROR:
                return False
            if self.status == AgentStatus.OFFLINE:
                return False
            return True
        except Exception as e:
            self.log_error(e, {"method": "health_check"})
            return False

    def get_config(self) -> Dict[str, Any]:
        """
        Get agent configuration

        Returns:
            Dict: Agent configuration
        """
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "config": self.config,
            "credentials_keys": list(self.credentials.keys())
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent to dictionary

        Returns:
            Dict: Agent as dictionary
        """
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "authenticated": self.is_authenticated,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "config": self.config
        }


class MarketplaceAgent(BaseAgent):
    """Base class for marketplace agents"""

    def __init__(self, name: str, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, AgentType.MARKETPLACE, credentials, config)

    async def post_product(self, product: Dict[str, Any]) -> bool:
        """
        Post a product to the marketplace
        
        Args:
            product: Product information
            
        Returns:
            bool: True if posting successful
        """
        raise NotImplementedError

    async def update_product(self, product_id: str, product: Dict[str, Any]) -> bool:
        """
        Update a product on the marketplace
        
        Args:
            product_id: ID of the product
            product: Updated product information
            
        Returns:
            bool: True if update successful
        """
        raise NotImplementedError

    async def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from the marketplace
        
        Args:
            product_id: ID of the product
            
        Returns:
            bool: True if deletion successful
        """
        raise NotImplementedError

    async def get_products(self) -> List[Dict[str, Any]]:
        """
        Get all products from the marketplace
        
        Returns:
            List: List of products
        """
        raise NotImplementedError


class MessagingAgent(BaseAgent):
    """Base class for messaging platform agents"""

    def __init__(self, name: str, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, AgentType.MESSAGING, credentials, config)

    async def send_message(self, chat_id: str, message: str) -> bool:
        """
        Send a message
        
        Args:
            chat_id: Chat ID
            message: Message content
            
        Returns:
            bool: True if sent successful
        """
        raise NotImplementedError

    async def handle_message(self, message: Dict[str, Any]) -> str:
        """
        Handle incoming message
        
        Args:
            message: Incoming message
            
        Returns:
            str: Response message
        """
        raise NotImplementedError

    async def get_messages(self, chat_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages from a chat
        
        Args:
            chat_id: Chat ID
            limit: Number of messages to retrieve
            
        Returns:
            List: List of messages
        """
        raise NotImplementedError


class SocialMediaAgent(BaseAgent):
    """Base class for social media agents"""

    def __init__(self, name: str, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, AgentType.SOCIAL, credentials, config)

    async def post_content(self, content: str, media: Optional[List[str]] = None) -> bool:
        """
        Post content to social media
        
        Args:
            content: Post content
            media: Optional media files
            
        Returns:
            bool: True if posting successful
        """
        raise NotImplementedError

    async def get_followers(self) -> List[Dict[str, Any]]:
        """
        Get followers list
        
        Returns:
            List: List of followers
        """
        raise NotImplementedError

    async def get_analytics(self) -> Dict[str, Any]:
        """
        Get account analytics
        
        Returns:
            Dict: Analytics data
        """
        raise NotImplementedError


class AffiliateAgent(BaseAgent):
    """Base class for affiliate marketing agents"""

    def __init__(self, name: str, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, AgentType.AFFILIATE, credentials, config)

    async def get_products(self) -> List[Dict[str, Any]]:
        """
        Get affiliate products
        
        Returns:
            List: List of products
        """
        raise NotImplementedError

    async def get_commissions(self) -> Dict[str, Any]:
        """
        Get commission information
        
        Returns:
            Dict: Commission data
        """
        raise NotImplementedError

    async def get_sales(self) -> List[Dict[str, Any]]:
        """
        Get sales history
        
        Returns:
            List: List of sales
        """
        raise NotImplementedError
