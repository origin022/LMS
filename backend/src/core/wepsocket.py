from fastapi import WebSocket
from typing import Dict, List
import asyncio

class ConnectionManager:
    def __init__(self):
        # Key: lecture_id (int), Value: List of WebSocket
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, lecture_id: int):
        await websocket.accept()
        if lecture_id not in self.active_connections:
            self.active_connections[lecture_id] = []
        self.active_connections[lecture_id].append(websocket)

    def disconnect(self, websocket: WebSocket, lecture_id: int):
        if lecture_id in self.active_connections:
            if websocket in self.active_connections[lecture_id]:
                self.active_connections[lecture_id].remove(websocket)
            if not self.active_connections[lecture_id]:
                del self.active_connections[lecture_id]

    async def broadcast_to_lecture(self, lecture_id: int, message: dict):
        if lecture_id not in self.active_connections:
            return

        connections = list(self.active_connections[lecture_id])
        
        async def send_to_one(connection: WebSocket):
            try:
                # Parallel send with a timeout for each connection
                await asyncio.wait_for(connection.send_json(message), timeout=5.0)
            except Exception:
                self.disconnect(connection, lecture_id)

        # We don't await this directly if we want the POST request to be super fast,
        # but gather here is fast because it's parallel.
        await asyncio.gather(*[send_to_one(c) for c in connections], return_exceptions=True)

manager = ConnectionManager()