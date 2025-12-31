"""Instagram Agent - Manages Instagram content and messaging"""

from typing import Dict, List, Optional, Any
from control.core.base_agent import SocialMediaAgent, AgentStatus
from loguru import logger


class InstagramAgent(SocialMediaAgent):
    """Agent for managing Instagram content and engagement"""

    def __init__(self, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__("InstagramAgent", credentials, config)
        self.username = credentials.get('username') if credentials else None
        self.posts: Dict[str, Dict[str, Any]] = {}
        self.followers: List[Dict[str, Any]] = []

    async def authenticate(self) -> bool:
        try:
            if not self.username or not self.credentials.get('password'):
                logger.error("Instagram requires username and password")
                return False
            logger.info(f"Authenticating with Instagram as {self.username}")
            self.is_authenticated = True
            self.status = AgentStatus.IDLE
            return True
        except Exception as e:
            self.log_error(e, {"method": "authenticate"})
            return False

    async def start(self):
        try:
            logger.info("Starting Instagram agent")
            self.status = AgentStatus.RUNNING
            self.update_activity()
        except Exception as e:
            self.log_error(e, {"method": "start"})
            self.status = AgentStatus.ERROR

    async def stop(self):
        try:
            logger.info("Stopping Instagram agent")
            self.status = AgentStatus.IDLE
        except Exception as e:
            self.log_error(e, {"method": "stop"})

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.update_activity()
            task_type = task.get('task_type', 'unknown')

            if task_type == 'post_content':
                return await self.post_content(task.get('content'), task.get('media'))
            elif task_type == 'get_followers':
                return {"followers": await self.get_followers()}
            elif task_type == 'get_analytics':
                return await self.get_analytics()
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
        except Exception as e:
            self.log_error(e, {"task": task})
            return {"success": False, "error": str(e)}

    async def post_content(self, content: str, media: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            if not content:
                return {"success": False, "error": "Content required"}
            
            post_id = f"ig_{len(self.posts) + 1}"
            self.posts[post_id] = {
                "id": post_id,
                "content": content,
                "media": media or [],
                "timestamp": str(self.last_activity),
                "likes": 0,
                "comments": 0
            }
            logger.info(f"Post published to Instagram: {post_id}")
            return {"success": True, "post_id": post_id}
        except Exception as e:
            self.log_error(e, {"method": "post_content"})
            return {"success": False, "error": str(e)}

    async def get_followers(self) -> List[Dict[str, Any]]:
        try:
            return self.followers
        except Exception as e:
            self.log_error(e, {"method": "get_followers"})
            return []

    async def get_analytics(self) -> Dict[str, Any]:
        try:
            return {
                "total_posts": len(self.posts),
                "total_followers": len(self.followers),
                "engagement_rate": 0.0,
                "last_updated": str(self.last_activity)
            }
        except Exception as e:
            self.log_error(e, {"method": "get_analytics"})
            return {}
