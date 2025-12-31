"""Torob Agent - Manages Torob marketplace"""

from typing import Dict, List, Optional, Any
from control.core.base_agent import MarketplaceAgent, AgentStatus
from loguru import logger


class TorobAgent(MarketplaceAgent):
    """Agent for managing Torob marketplace (ترب)"""

    def __init__(self, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__("TorobAgent", credentials, config)
        self.base_url = "https://torob.com"
        self.listings: Dict[str, Dict[str, Any]] = {}

    async def authenticate(self) -> bool:
        try:
            if not self.credentials.get('seller_id') or not self.credentials.get('token'):
                logger.error("Torob requires seller_id and token")
                return False
            logger.info(f"Authenticating with Torob seller {self.credentials.get('seller_id')}")
            self.is_authenticated = True
            self.status = AgentStatus.IDLE
            return True
        except Exception as e:
            self.log_error(e, {"method": "authenticate"})
            return False

    async def start(self):
        try:
            logger.info("Starting Torob agent")
            self.status = AgentStatus.RUNNING
            self.update_activity()
        except Exception as e:
            self.log_error(e, {"method": "start"})
            self.status = AgentStatus.ERROR

    async def stop(self):
        try:
            logger.info("Stopping Torob agent")
            self.status = AgentStatus.IDLE
        except Exception as e:
            self.log_error(e, {"method": "stop"})

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.update_activity()
            task_type = task.get('task_type', 'unknown')

            if task_type == 'post_product':
                return await self.post_product(task.get('data', {}))
            elif task_type == 'update_product':
                return await self.update_product(task.get('product_id'), task.get('data', {}))
            elif task_type == 'delete_product':
                return await self.delete_product(task.get('product_id'))
            elif task_type == 'get_products':
                return {"products": await self.get_products()}
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
        except Exception as e:
            self.log_error(e, {"task": task})
            return {"success": False, "error": str(e)}

    async def post_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        try:
            required_fields = ['title', 'description', 'category', 'price']
            if not all(field in product for field in required_fields):
                return {"success": False, "error": "Missing required fields"}

            product_id = f"torob_{len(self.listings) + 1}"
            self.listings[product_id] = {
                **product,
                "id": product_id,
                "status": "active",
                "posted_at": str(self.last_activity)
            }
            logger.info(f"Product posted to Torob: {product_id}")
            return {
                "success": True,
                "product_id": product_id,
                "url": f"{self.base_url}/detail/{product_id}"
            }
        except Exception as e:
            self.log_error(e, {"method": "post_product"})
            return {"success": False, "error": str(e)}

    async def update_product(self, product_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if product_id not in self.listings:
                return {"success": False, "error": "Product not found"}
            self.listings[product_id].update(product)
            logger.info(f"Product updated on Torob: {product_id}")
            return {"success": True, "product_id": product_id}
        except Exception as e:
            self.log_error(e, {"method": "update_product"})
            return {"success": False, "error": str(e)}

    async def delete_product(self, product_id: str) -> Dict[str, Any]:
        try:
            if product_id not in self.listings:
                return {"success": False, "error": "Product not found"}
            del self.listings[product_id]
            logger.info(f"Product deleted from Torob: {product_id}")
            return {"success": True, "product_id": product_id}
        except Exception as e:
            self.log_error(e, {"method": "delete_product"})
            return {"success": False, "error": str(e)}

    async def get_products(self) -> List[Dict[str, Any]]:
        try:
            return list(self.listings.values())
        except Exception as e:
            self.log_error(e, {"method": "get_products"})
            return []
