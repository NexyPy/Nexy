import asyncio
from typing import List, Optional
from fastapi import WebSocket, WebSocketDisconnect

class HMRManager:
    _instance = None
    _connections: List[WebSocket] = []
    loop: Optional[asyncio.AbstractEventLoop] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HMRManager, cls).__new__(cls)
        return cls._instance

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast_reload(self, path: str = ""):
        """Sends a reload signal to all connected clients."""
        disconnected = []
        for connection in self._connections:
            try:
                await connection.send_json({
                    "type": "nexy:reload",
                    "path": path
                })
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

HMR_MANAGER = HMRManager()
