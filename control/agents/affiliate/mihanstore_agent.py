"""MihanStore Agent - Manages MihanStore affiliate store"""

from typing import Dict, List, Optional, Any
from control.core.base_agent import AffiliateAgent, AgentStatus
from loguru import logger


class MihanStoreAgent(AffiliateAgent):
    """Agent for managing MihanStore affiliate (میهن‌استور)"""

    def __init__(self, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__("MihanStoreAgent", credentials, config)
        self.base_url = "https://mihanstore.net/partner"
        self.products: Dict[str, Dict[str, Any]] = {}
        self.sales: List[Dict[str, Any]] = []
        self.total_commission = 0.0

    async def authenticate(self) -> bool:
        try:
            if not self.credentials.get('shop_id') or not self.credentials.get('token'):
                logger.error("MihanStore requires shop_id and token")
                return False
            logger.info(f"Authenticating with MihanStore shop {self.credentials.get('shop_id')}")
            self.is_authenticated = True
            self.status = AgentStatus.IDLE
            return True
        except Exception as e:
            self.log_error(e, {"method": "authenticate"})
            return False

    async def start(self):
        try:
            logger.info("Starting MihanStore agent")
            self.status = AgentStatus.RUNNING
            self.update_activity()
        except Exception as e:
            self.log_error(e, {"method": "start"})
            self.status = AgentStatus.ERROR

    async def stop(self):
        try:
            logger.info("Stopping MihanStore agent")
            self.status = AgentStatus.IDLE
        except Exception as e:
            self.log_error(e, {"method": "stop"})

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.update_activity()
            task_type = task.get('task_type', 'unknown')

            if task_type == 'get_products':
                return {"products": await self.get_products()}
            elif task_type == 'get_sales':
                return {"sales": await self.get_sales()}
            elif task_type == 'get_commissions':
                return await self.get_commissions()
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
        except Exception as e:
            self.log_error(e, {"task": task})
            return {"success": False, "error": str(e)}

    async def get_products(self) -> List[Dict[str, Any]]:
        try:
            return list(self.products.values())
        except Exception as e:
            self.log_error(e, {"method": "get_products"})
            return []

    async def get_sales(self) -> List[Dict[str, Any]]:
        try:
            return self.sales
        except Exception as e:
            self.log_error(e, {"method": "get_sales"})
            return []

    async def get_commissions(self) -> Dict[str, Any]:
        try:
            return {
                "total_commission": self.total_commission,
                "commission_rate": 0.10,
                "last_updated": str(self.last_activity)
            }
        except Exception as e:
            self.log_error(e, {"method": "get_commissions"})
            return {"total_commission": 0, "error": str(e)}
