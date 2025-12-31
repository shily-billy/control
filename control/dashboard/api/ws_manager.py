"""WebSocket connection manager"""

from fastapi import WebSocket
from loguru import logger

class WSManager:
    def __init__(self):
        self.connections: set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.add(ws)
        logger.info(f"WS connected. total={len(self.connections)}")

    async def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)
        logger.info(f"WS disconnected. total={len(self.connections)}")

    async def broadcast_json(self, payload: dict):
        dead = []
        for ws in self.connections:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)
