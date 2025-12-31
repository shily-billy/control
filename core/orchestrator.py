"""Central orchestrator for managing all agents"""
import asyncio
from typing import Dict, List
from core.logger import setup_logger
from core.event_bus import EventBus
from core.task_scheduler import TaskScheduler

logger = setup_logger(__name__)

class Orchestrator:
    """Central controller for all agents"""
    
    def __init__(self):
        self.agents: Dict[str, any] = {}
        self.event_bus = EventBus()
        self.scheduler = TaskScheduler()
        self.running = False
        logger.info("Orchestrator initialized")
    
    async def start(self):
        """Start the orchestrator and all agents"""
        logger.info("Starting orchestrator...")
        self.running = True
        
        # Start event bus
        await self.event_bus.start()
        
        # Start scheduler
        self.scheduler.start()
        
        # Load and start agents
        await self._load_agents()
        
        logger.info(f"Orchestrator started with {len(self.agents)} agents")
    
    async def _load_agents(self):
        """Load all configured agents"""
        # Will be populated with actual agents
        logger.info("Loading agents...")
        # TODO: Load agents from config
        pass
    
    async def run(self):
        """Main run loop"""
        while self.running:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Stop all agents and cleanup"""
        logger.info("Stopping orchestrator...")
        self.running = False
        
        # Stop all agents
        for name, agent in self.agents.items():
            logger.info(f"Stopping agent: {name}")
            await agent.stop()
        
        # Stop scheduler
        self.scheduler.stop()
        
        # Stop event bus
        await self.event_bus.stop()
        
        logger.info("Orchestrator stopped")
    
    def register_agent(self, name: str, agent):
        """Register a new agent"""
        self.agents[name] = agent
        logger.info(f"Agent registered: {name}")
