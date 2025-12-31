"""Twitter Agent - Manages Twitter/X content and engagement"""

from typing import Dict, List, Optional, Any
from control.core.base_agent import SocialMediaAgent, AgentStatus
from loguru import logger


class TwitterAgent(SocialMediaAgent):
    """Agent for managing Twitter/X content and engagement"""

    def __init__(self, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__("TwitterAgent", credentials, config)
        self.api_key = credentials.get('api_key') if credentials else None
        self.tweets: Dict[str, Dict[str, Any]] = {}
        self.followers: List[Dict[str, Any]] = []

    async def authenticate(self) -> bool:
        try:
            if not self.api_key:
                logger.error("Twitter requires api_key")
                return False
            logger.info("Authenticating with Twitter/X")
            self.is_authenticated = True
            self.status = AgentStatus.IDLE
            return True
        except Exception as e:
            self.log_error(e, {"method": "authenticate"})
            return False

    async def start(self):
        try:
            logger.info("Starting Twitter agent")
            self.status = AgentStatus.RUNNING
            self.update_activity()
        except Exception as e:
            self.log_error(e, {"method": "start"})
            self.status = AgentStatus.ERROR

    async def stop(self):
        try:
            logger.info("Stopping Twitter agent")
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
            
            tweet_id = f"tw_{len(self.tweets) + 1}"
            self.tweets[tweet_id] = {
                "id": tweet_id,
                "content": content,
                "media": media or [],
                "timestamp": str(self.last_activity),
                "retweets": 0,
                "likes": 0,
                "replies": 0
            }
            logger.info(f"Tweet posted to Twitter: {tweet_id}")
            return {"success": True, "tweet_id": tweet_id}
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
                "total_tweets": len(self.tweets),
                "total_followers": len(self.followers),
                "engagement_rate": 0.0,
                "last_updated": str(self.last_activity)
            }
        except Exception as e:
            self.log_error(e, {"method": "get_analytics"})
            return {}
