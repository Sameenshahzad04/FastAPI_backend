# utils/websocket_manager.py

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json

class ConnectionManager:
    def __init__(self):
       
        # {client_id: websocket} - Track all active connections
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: int):
        
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: int):
        
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, message: dict, client_id: int):
        
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))
    
    async def broadcast(self, message: dict, exclude_id: int = None):
      
        message_json = json.dumps(message)
        for cid, conn in self.active_connections.items():
            if exclude_id is None or cid != exclude_id:
                await conn.send_text(message_json)
    async def send_to_client(self, message: dict, client_id: int):
       
        if client_id in self.active_connections:
            
            await self.active_connections[client_id].send_text(json.dumps(message))
    
    
    def get_active_users(self):
      
        return list(self.active_connections.keys())

manager = ConnectionManager()