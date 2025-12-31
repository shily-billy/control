"""Task scheduler for automated agent tasks"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from core.logger import setup_logger

logger = setup_logger(__name__)

class TaskScheduler:
    """Scheduler for periodic and scheduled tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        logger.info("TaskScheduler initialized")
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("TaskScheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("TaskScheduler stopped")
    
    def add_interval_job(self, func, seconds: int, job_id: str = None):
        """Add a job that runs at fixed intervals"""
        trigger = IntervalTrigger(seconds=seconds)
        self.scheduler.add_job(func, trigger, id=job_id)
        logger.info(f"Interval job added: {job_id or 'unnamed'} ({seconds}s)")
    
    def add_cron_job(self, func, cron_expr: str, job_id: str = None):
        """Add a cron-style scheduled job"""
        trigger = CronTrigger.from_crontab(cron_expr)
        self.scheduler.add_job(func, trigger, id=job_id)
        logger.info(f"Cron job added: {job_id or 'unnamed'} ({cron_expr})")
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        self.scheduler.remove_job(job_id)
        logger.info(f"Job removed: {job_id}")
