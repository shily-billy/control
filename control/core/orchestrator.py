"""Orchestrator - Manages and coordinates all agents"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
import asyncio

from .base_agent import BaseAgent, AgentStatus


class Orchestrator:
    """Main orchestrator for managing all agents"""

    def __init__(self):
        """
        Initialize the orchestrator
        """
        self.agents: Dict[str, BaseAgent] = {}
        self.running_agents: List[str] = []
        self.started_at = datetime.now()
        self.is_running = False

    def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent with the orchestrator

        Args:
            agent: Agent instance to register

        Returns:
            bool: True if registration successful
        """
        try:
            if agent.name in self.agents:
                logger.warning(f"Agent {agent.name} already registered. Overwriting.")
            self.agents[agent.name] = agent
            logger.info(f"Agent {agent.name} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent.name}: {e}")
            return False

    def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent

        Args:
            agent_name: Name of the agent to unregister

        Returns:
            bool: True if unregistration successful
        """
        try:
            if agent_name in self.agents:
                del self.agents[agent_name]
                if agent_name in self.running_agents:
                    self.running_agents.remove(agent_name)
                logger.info(f"Agent {agent_name} unregistered")
                return True
            logger.warning(f"Agent {agent_name} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_name}: {e}")
            return False

    async def start_agent(self, agent_name: str) -> bool:
        """
        Start a specific agent

        Args:
            agent_name: Name of the agent to start

        Returns:
            bool: True if agent started successfully
        """
        try:
            if agent_name not in self.agents:
                logger.error(f"Agent {agent_name} not found")
                return False

            agent = self.agents[agent_name]

            # Authenticate if not already authenticated
            if not agent.is_authenticated:
                if not await agent.authenticate():
                    logger.error(f"Failed to authenticate {agent_name}")
                    return False

            # Start the agent
            await agent.start()
            agent.status = AgentStatus.RUNNING
            self.running_agents.append(agent_name)
            logger.info(f"Agent {agent_name} started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start agent {agent_name}: {e}")
            if agent_name in self.agents:
                self.agents[agent_name].log_error(e, {"method": "start_agent"})
            return False

    async def stop_agent(self, agent_name: str) -> bool:
        """
        Stop a specific agent

        Args:
            agent_name: Name of the agent to stop

        Returns:
            bool: True if agent stopped successfully
        """
        try:
            if agent_name not in self.agents:
                logger.error(f"Agent {agent_name} not found")
                return False

            agent = self.agents[agent_name]
            await agent.stop()
            agent.status = AgentStatus.IDLE
            if agent_name in self.running_agents:
                self.running_agents.remove(agent_name)
            logger.info(f"Agent {agent_name} stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop agent {agent_name}: {e}")
            if agent_name in self.agents:
                self.agents[agent_name].log_error(e, {"method": "stop_agent"})
            return False

    async def queue_task(self, agent_name: str, task: Dict[str, Any]) -> bool:
        """
        Queue a task for an agent

        Args:
            agent_name: Name of the agent
            task: Task to queue

        Returns:
            bool: True if task queued successfully
        """
        try:
            if agent_name not in self.agents:
                logger.error(f"Agent {agent_name} not found")
                return False

            agent = self.agents[agent_name]
            await agent.queue_task(task)
            return True

        except Exception as e:
            logger.error(f"Failed to queue task for {agent_name}: {e}")
            return False

    async def start_all_agents(self) -> Dict[str, bool]:
        """
        Start all registered agents

        Returns:
            Dict: Status of each agent
        """
        results = {}
        tasks = []
        for agent_name in self.agents.keys():
            tasks.append(self.start_agent(agent_name))
            results[agent_name] = False

        try:
            outcomes = await asyncio.gather(*tasks, return_exceptions=True)
            for agent_name, outcome in zip(self.agents.keys(), outcomes):
                results[agent_name] = outcome if isinstance(outcome, bool) else False
        except Exception as e:
            logger.error(f"Error starting all agents: {e}")

        self.is_running = all(results.values())
        return results

    async def stop_all_agents(self) -> Dict[str, bool]:
        """
        Stop all running agents

        Returns:
            Dict: Status of each agent
        """
        results = {}
        tasks = []
        for agent_name in list(self.running_agents):
            tasks.append(self.stop_agent(agent_name))
            results[agent_name] = False

        try:
            outcomes = await asyncio.gather(*tasks, return_exceptions=True)
            agent_names = list(self.running_agents)
            for agent_name, outcome in zip(agent_names, outcomes):
                results[agent_name] = outcome if isinstance(outcome, bool) else False
        except Exception as e:
            logger.error(f"Error stopping all agents: {e}")

        self.is_running = False
        return results

    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific agent

        Args:
            agent_name: Name of the agent

        Returns:
            Dict: Agent status or None if not found
        """
        if agent_name not in self.agents:
            logger.warning(f"Agent {agent_name} not found")
            return None
        return asyncio.run(self.agents[agent_name].get_status())

    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all agents

        Returns:
            Dict: Status of all agents
        """
        statuses = {}
        for agent_name in self.agents.keys():
            status = self.get_agent_status(agent_name)
            if status:
                statuses[agent_name] = status
        return statuses

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """
        Get orchestrator status

        Returns:
            Dict: Orchestrator status information
        """
        return {
            "total_agents": len(self.agents),
            "running_agents": len(self.running_agents),
            "is_running": self.is_running,
            "started_at": self.started_at.isoformat(),
            "uptime_seconds": (datetime.now() - self.started_at).total_seconds(),
            "agents": self.get_all_agents_status()
        }

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents

        Returns:
            List: List of agent information
        """
        agents_list = []
        for agent in self.agents.values():
            agents_list.append({
                "name": agent.name,
                "type": agent.agent_type.value,
                "status": agent.status.value,
                "authenticated": agent.is_authenticated
            })
        return agents_list

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """
        Get agent instance

        Args:
            agent_name: Name of the agent

        Returns:
            BaseAgent: Agent instance or None if not found
        """
        return self.agents.get(agent_name)
