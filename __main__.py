"""Main entry point for Control system"""
import asyncio
from core.orchestrator import Orchestrator
from core.logger import setup_logger

logger = setup_logger(__name__)

async def main():
    """Start the Control system"""
    logger.info("Starting Control Multi-Agent System...")
    
    orchestrator = Orchestrator()
    await orchestrator.start()
    
    try:
        # Keep running
        await orchestrator.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await orchestrator.stop()
    except Exception as e:
        logger.error(f"Error: {e}")
        await orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
