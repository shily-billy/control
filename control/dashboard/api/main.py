"""FastAPI app entrypoint"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from control.dashboard.api.ws_manager import WSManager
from control.dashboard.api.routes import router

app = FastAPI(title="control")
ws_manager = WSManager()

app.include_router(router)

@app.get("/health")
async def health():
    return {"ok": True}

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            # keep-alive / allow client messages
            await ws.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws)
