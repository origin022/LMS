from fastapi import WebSocket
from typing import Dict, List
import asyncio
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, lecture_id: int):
        await websocket.accept()
        if lecture_id not in self.active_connections:
            self.active_connections[lecture_id] = []
        self.active_connections[lecture_id].append(websocket)

    def disconnect(self, websocket: WebSocket, lecture_id: int):
        if lecture_id in self.active_connections:
            self.active_connections[lecture_id].remove(websocket)
            if not self.active_connections[lecture_id]:
                del self.active_connections[lecture_id]
    async def broadcast_to_lecture(self, lecture_id: int, message: dict):
        if lecture_id not in self.active_connections:
            return

        connections = list(self.active_connections[lecture_id])

        async def send_safe(connection: WebSocket):
            try:
                await asyncio.wait_for(connection.send_json(message), timeout=2)
            except Exception:
                self.disconnect(connection, lecture_id)

        await asyncio.gather(*[send_safe(c) for c in connections], return_exceptions=True)


    async def connect(self, websocket: WebSocket, lecture_id: int):
        await websocket.accept()

        if lecture_id not in self.active_connections:
            self.active_connections[lecture_id] = []

        self.active_connections[lecture_id] = [
            ws for ws in self.active_connections[lecture_id]
            if ws.client_state.name == "CONNECTED"
        ]

        self.active_connections[lecture_id].append(websocket)

manager = ConnectionManager()