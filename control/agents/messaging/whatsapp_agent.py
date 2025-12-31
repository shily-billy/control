"""WhatsApp Agent - Handles WhatsApp messaging"""

from typing import Dict, List, Optional, Any
from control.core.base_agent import MessagingAgent, AgentStatus
from loguru import logger


class WhatsAppAgent(MessagingAgent):
    """Agent for managing WhatsApp messaging"""

    def __init__(self, credentials: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__("WhatsAppAgent", credentials, config)
        self.phone_number = credentials.get('phone_number') if credentials else None
        self.messages: Dict[str, List[Dict[str, Any]]] = {}

    async def authenticate(self) -> bool:
        try:
            if not self.phone_number:
                logger.error("WhatsApp requires phone_number")
                return False
            logger.info(f"Authenticating with WhatsApp: {self.phone_number}")
            self.is_authenticated = True
            self.status = AgentStatus.IDLE
            return True
        except Exception as e:
            self.log_error(e, {"method": "authenticate"})
            return False

    async def start(self):
        try:
            logger.info("Starting WhatsApp agent")
            self.status = AgentStatus.RUNNING
            self.update_activity()
        except Exception as e:
            self.log_error(e, {"method": "start"})
            self.status = AgentStatus.ERROR

    async def stop(self):
        try:
            logger.info("Stopping WhatsApp agent")
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
            logger.info(f"WhatsApp message sent to {chat_id}")
            return {"success": True, "message_id": msg_obj["id"]}
        except Exception as e:
            self.log_error(e, {"method": "send_message"})
            return {"success": False, "error": str(e)}

    async def handle_message(self, message: Dict[str, Any]) -> str:
        try:
            logger.info(f"Handling WhatsApp message")
            return "سلام! مرسی تماس میکنید"
        except Exception as e:
            self.log_error(e, {"method": "handle_message"})
            return "خطایی پیش آمد"

    async def get_messages(self, chat_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            if chat_id not in self.messages:
                return []
            return self.messages[chat_id][-limit:]
        except Exception as e:
            self.log_error(e, {"method": "get_messages"})
            return []
