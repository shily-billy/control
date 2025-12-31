"""Telegram Agent - Handles auto-responses and messaging"""

from typing import Dict, List, Optional, Any
from control.core.base_agent import MessagingAgent, AgentStatus
from loguru import logger


class TelegramAgent(MessagingAgent):
    """Agent for managing Telegram messaging and auto-responses"""

    def __init__(self, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__("TelegramAgent", credentials, config)
        self.bot_token = credentials.get('bot_token') if credentials else None
        self.messages: Dict[str, List[Dict[str, Any]]] = {}
        self.auto_responses: Dict[str, str] = config.get('auto_responses', {}) if config else {}

    async def authenticate(self) -> bool:
        try:
            if not self.bot_token:
                logger.error("Telegram requires bot_token")
                return False
            logger.info("Authenticating with Telegram")
            self.is_authenticated = True
            self.status = AgentStatus.IDLE
            return True
        except Exception as e:
            self.log_error(e, {"method": "authenticate"})
            return False

    async def start(self):
        try:
            logger.info("Starting Telegram agent")
            self.status = AgentStatus.RUNNING
            self.update_activity()
        except Exception as e:
            self.log_error(e, {"method": "start"})
            self.status = AgentStatus.ERROR

    async def stop(self):
        try:
            logger.info("Stopping Telegram agent")
            self.status = AgentStatus.IDLE
        except Exception as e:
            self.log_error(e, {"method": "stop"})

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.update_activity()
            task_type = task.get('task_type', 'unknown')

            if task_type == 'send_message':
                return await self.send_message(task.get('chat_id'), task.get('message'))
            elif task_type == 'handle_message':
                return {"response": await self.handle_message(task.get('message'))}
            elif task_type == 'get_messages':
                return {"messages": await self.get_messages(task.get('chat_id'))}
            elif task_type == 'set_auto_response':
                return await self.set_auto_response(task.get('keyword'), task.get('response'))
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
        except Exception as e:
            self.log_error(e, {"task": task})
            return {"success": False, "error": str(e)}

    async def send_message(self, chat_id: str, message: str) -> Dict[str, Any]:
        try:
            if not chat_id or not message:
                return {"success": False, "error": "chat_id and message required"}

            if chat_id not in self.messages:
                self.messages[chat_id] = []

            msg_obj = {
                "id": len(self.messages[chat_id]),
                "text": message,
                "timestamp": str(self.last_activity),
                "direction": "outgoing"
            }
            self.messages[chat_id].append(msg_obj)
            logger.info(f"Message sent to Telegram chat {chat_id}")

            return {"success": True, "message_id": msg_obj["id"]}
        except Exception as e:
            self.log_error(e, {"method": "send_message"})
            return {"success": False, "error": str(e)}

    async def handle_message(self, message: Dict[str, Any]) -> str:
        try:
            text = message.get('text', '').lower()
            
            # Check for auto-response keywords
            for keyword, response in self.auto_responses.items():
                if keyword.lower() in text:
                    logger.info(f"Auto-response triggered for keyword: {keyword}")
                    return response

            # Default response
            return "سلام! متشکرم که با ما تماس گرفتید."
        except Exception as e:
            self.log_error(e, {"method": "handle_message"})
            return "متاسفانه خطایی پیش آمد."

    async def get_messages(self, chat_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            if chat_id not in self.messages:
                return []
            return self.messages[chat_id][-limit:]
        except Exception as e:
            self.log_error(e, {"method": "get_messages"})
            return []

    async def set_auto_response(self, keyword: str, response: str) -> Dict[str, Any]:
        try:
            if not keyword or not response:
                return {"success": False, "error": "keyword and response required"}
            self.auto_responses[keyword] = response
            logger.info(f"Auto-response set for keyword: {keyword}")
            return {"success": True, "keyword": keyword}
        except Exception as e:
            self.log_error(e, {"method": "set_auto_response"})
            return {"success": False, "error": str(e)}
